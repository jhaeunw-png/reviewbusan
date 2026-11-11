import time

import pandas as pd
import requests
from tqdm import tqdm


url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
form_data = {
    "arrSggSidoCd[]": "26",
    "txtSGG_CD": "",
    "txtSIDO_ARR": "1",
    "txtADONG_ARR": "",
    "SGG_CD": "26",
    "SIDO_ARR": "26",
    "BASE_YM1": "202511",
    "BASE_YM2": "202610",
    "srchAreaDate": "1",
    "tabDiv": "1",
    "qid": "BDT_01_03_001",
}

# 수집 기간: 2018년 1월 ~ 2026년 10월, 요청당 최대 12개월
months = pd.period_range("2018-01", "2026-10", freq="M")

dfs = []
error_periods = []
empty_periods = []
for index in tqdm(range(0, len(months), 12), desc="방문자 자료 수집"):
    start_ym = months[index].strftime("%Y%m")
    end_ym = months[min(index + 11, len(months) - 1)].strftime("%Y%m")
    form_data.update({"BASE_YM1": start_ym, "BASE_YM2": end_ym})
    period = f"{start_ym}~{end_ym}"

    try:
        response = requests.post(url, data=form_data, timeout=60)
        response.raise_for_status()
        data = response.json()
        rows = data["list"]
        if not isinstance(rows, list):
            raise ValueError("응답의 list가 배열이 아닙니다.")
        if not rows:
            empty_periods.append(period)
        else:
            df = pd.DataFrame(rows)
            df = df[
                [
                    "BASE_DATE",
                    "SIDO_NM",
                    "TOU_DIV_NM",
                    "TOU_NUM",
                ]
            ]
            dfs.append(df)
            time.sleep(0.1)
    except (requests.RequestException, ValueError, KeyError) as error:
        error_periods.append(period)
        tqdm.write(f"{period} 수집 실패: {error}")

    # 외국인 자료는 2020년부터 별도 조회한다.
    foreign_start = max(months[index], pd.Period("2020-01", freq="M"))
    if foreign_start > months[min(index + 11, len(months) - 1)]:
        continue

    foreign_form_data = form_data.copy()
    foreign_form_data.update({
        "SGG_CD": "",
        "BASE_YM1": foreign_start.strftime("%Y%m"),
        "tabDiv": "3",
        "qid": "BDT_SKT_FRG_02_01_001",
    })
    try:
        response = requests.post(url, data=foreign_form_data, timeout=60)
        response.raise_for_status()
        data = response.json()
        rows = data["list"]
        if not isinstance(rows, list) or not rows:
            raise ValueError("외국인 응답의 list가 비어 있거나 배열이 아닙니다.")

        foreign_df = pd.DataFrame(rows)
        foreign_df = foreign_df[
            [
                "BASE_DATE",
                "SIDO_NM",
                "TOU_DIV_NM",
                "TOU_NUM",
            ]
        ]
        foreign_df["SIDO_NM"] = "부산광역시 " + foreign_df["SIDO_NM"].str.replace(
            r"^부산광역시\s+", "", regex=True
        )
        dfs.append(foreign_df)
        time.sleep(0.1)
    except (requests.RequestException, ValueError, KeyError) as error:
        error_periods.append(f"외국인 {period}")
        tqdm.write(f"외국인 {period} 수집 실패: {error}")

if not dfs:
    raise RuntimeError(f"수집된 데이터가 없습니다. 실패 구간: {error_periods}, 빈 구간: {empty_periods}")
if error_periods:
    raise RuntimeError(f"일부 구간의 수집이 실패해 기존 CSV를 덮어쓰지 않았습니다: {error_periods}")

result_df = pd.concat(dfs, ignore_index=True)
keys = ["BASE_DATE", "SIDO_NM"]
local = result_df.loc[
    result_df["TOU_DIV_NM"].eq("현지인방문자(a)"), keys + ["TOU_NUM"]
].rename(columns={"TOU_NUM": "local_cnt"})
outside = result_df.loc[
    result_df["TOU_DIV_NM"].eq("외지인방문자(b)"), keys + ["TOU_NUM"]
].rename(columns={"TOU_NUM": "outside_cnt"})
foreign = result_df.loc[
    result_df["TOU_DIV_NM"].eq("외국인방문자(c)"), keys + ["TOU_NUM"]
].rename(columns={"TOU_NUM": "foreign_cnt"})

# 외국인 응답이 없는 월·구군에도 행을 두되, 방문자 수는 결측으로 남긴다.
combined = local.merge(outside, on=keys, validate="one_to_one").merge(
    foreign, on=keys, how="left", validate="one_to_one"
)
missing_foreign = combined["foreign_cnt"].isna()
placeholder = combined.loc[missing_foreign, keys].copy()
placeholder["TOU_DIV_NM"] = "외국인방문자(c)"
placeholder["TOU_NUM"] = pd.NA

total = combined[keys].copy()
total["TOU_DIV_NM"] = "전체방문자(a+b+c)"
total["TOU_NUM"] = (
    pd.to_numeric(combined["local_cnt"])
    + pd.to_numeric(combined["outside_cnt"])
    + pd.to_numeric(combined["foreign_cnt"])
)

result_df = result_df.loc[~result_df["TOU_DIV_NM"].eq("전체방문자(a+b)")].copy()
result_df = pd.concat(
    [result_df, placeholder[result_df.columns], total[result_df.columns]],
    ignore_index=True,
)
result_df["TOU_DIV_NM"] = result_df["TOU_DIV_NM"].replace({
    "현지인방문자(a)": "현지인",
    "외지인방문자(b)": "외지인",
    "외국인방문자(c)": "외국인",
    "전체방문자(a+b+c)": "전체(a+b+c)",
})
result_df = result_df.sort_values(keys + ["TOU_DIV_NM"]).reset_index(drop=True)
result_df.to_csv(
    "sources/results/방문자_자료.csv",
    index=False,
    encoding="utf-8-sig",
)

print(f"저장 행 수: {len(result_df):,}")
print(f"외국인 미수집 NULL 행 수: {len(placeholder):,}")
print(f"데이터가 없는 구간: {empty_periods}")
