import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine
from tqdm import tqdm


load_dotenv("./database/.env")

db_info = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
    f"@{os.getenv('HOST', 'localhost')}:{os.getenv('DB_PORT')}"
    f"/{os.getenv('MYSQL_DATABASE')}"
)
engine = create_engine(db_info)
stations = pd.read_sql(
    "SELECT sgg_cd, sgg_nm FROM sigungu WHERE sido_cd = '26' ORDER BY sgg_cd",
    con=engine,
)
engine.dispose()
if len(stations) != 16:
    raise ValueError(f"부산 구·군이 16개가 아닙니다: {len(stations)}개")

url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
form_data = {
    "SGG_CD": "26440",
    "SGG_NM": "부산광역시 강서구",
    "BASE_YM1": "202509",
    "BASE_YM2": "202509",
    "tabDiv": "3",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_006_01",
    "dnname": "숙박방문자 비율 추이(외지인)",
}

# 기존 방문자 자료와 같은 기간. 매 요청은 한 구·군의 한 달만 조회한다.
last_month = pd.Timestamp.today().to_period("M") - 1
months = pd.period_range("2018-01", last_month, freq="M")

rows = []
empty_periods = []
error_periods = []
tasks = (
    (month, station.sgg_cd, station.sgg_nm)
    for month in months
    for station in stations.itertuples(index=False)
)
for month, sgg_cd, sgg_nm in tqdm(
    tasks, total=len(months) * len(stations), desc="외지인 숙박방문자 비율 수집"
):
    base_ym = month.strftime("%Y%m")
    form_data.update({
        "SGG_CD": sgg_cd,
        "SGG_NM": f"부산광역시 {sgg_nm}",
        "BASE_YM1": base_ym,
        "BASE_YM2": base_ym,
    })

    try:
        response = requests.post(url, data=form_data, timeout=60)
        response.raise_for_status()
        data = response.json()["list"]
        if not isinstance(data, list):
            raise ValueError("응답의 list가 배열이 아닙니다.")
        if not data:
            empty_periods.append((base_ym, sgg_cd))
            continue

        df = pd.DataFrame(data)
        district = df.loc[df["TOU_DIV_NM"].eq(sgg_nm)]
        if len(district) != 1:
            raise ValueError(f"{sgg_nm} 응답 행이 {len(district)}개입니다.")
        rows.append({
            "SGG_CD": sgg_cd,
            "YEAR_MONTH": month.strftime("%Y-%m"),
            "EXT_TOU_NUM": district.iloc[0]["EXT_TOU_NUM"],
        })
        time.sleep(0.1)
    except (requests.RequestException, ValueError, KeyError) as error:
        error_periods.append((base_ym, sgg_cd, str(error)))

if error_periods:
    raise RuntimeError(f"수집 실패로 CSV를 덮어쓰지 않았습니다: {error_periods}")
if not rows:
    raise RuntimeError("수집된 숙박방문자 비율 데이터가 없습니다.")

result_df = pd.DataFrame(rows)
result_df.to_csv(
    "sources/results/숙박방문자_비율.csv", index=False, encoding="utf-8-sig"
)
print(f"저장 행 수: {len(result_df):,}")
print(f"데이터가 없는 월·구군: {empty_periods}")
