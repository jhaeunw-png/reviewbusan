import requests
import time
import random
import pandas as pd
from tqdm.auto import tqdm
from pathlib import Path

# 대중교통이용인원
# https://www.stcis.go.kr/pivotIndi/wpsPivotIndicator.do?siteGb=P&indiClss=IC05

# ==========================================
# 1. 기본 설정
# ==========================================

url = "https://www.stcis.go.kr/pivotIndi/indicatorPivotAjax.do"

output_dir = Path("sources/results/대중교통이용인원수집")
output_dir.mkdir(parents=True, exist_ok=True)

data = {
    "indiCd": "Z01720",
    "siteGb": "P",
    "searchDateGubun": "2",
    "searchFromYear": "2025",
    "searchToYear": "2025",
    "searchFromMonth": "2026-09",
    "searchToMonth": "2026-09",
    "searchFromDay": "2026-10-17",
    "searchToDay": "2026-10-17",
    "searchAreaGubun": "2",
    "zoneSd": "26",
    "zoneSgg": (
        "26440,26410,26710,26290,26170,26260,"
        "26230,26320,26530,26380,26140,26500,"
        "26470,26200,26110,26350"
    ),
    "zoneEmd": "",
    "zoneDstrct": "",
    "selectZoneSd": "26",
    "selectZoneSgg": "",
    "tcboId": "",
    "excclcAreaCd": "",
    "routeId": "",
    "routeSdCd": "",
    "routeSggCd": "",
    "daybyTblNm": "DM_PUBTRF_USESTF_020",
    "mnbyTblNm": "DM_MMBY_PUBTRF_USESTF_020",
    "yrbyTblNm": "DM_YRBY_PUBTRF_USESTF_020",
    "dstrctTblNm": "DM_DCTBY_PUBTRF_USESTF_T ",
    "mnbyDstrctTblNm": "DM_MMBY_DCTBY_PUBTRF_USESTF_T",
    "yrbyDstrctTblNm": "DM_YRBY_DCTBY_PUBTRF_USESTF_T",
}

# ddOption[] 순서 및 빈 값 유지
dd_options = [
    "",
    "",
    "DSTRCT",
    "OPRAT_DATE",
    "",
    "SD_CD",
    "SGG_CD",
    "USE_AREA_CD",
    "YYYY",
    "YYYYMM",
    "USE_STF",
    "USER_TYPE_CD",
]

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.stcis.go.kr/",
}

# ==========================================
# 2. 수집 기간 설정
# ==========================================

months = pd.period_range(
    start="2020-10",
    end="2026-09",
    freq="M"
)

results = []
failed_months = []

# ==========================================
# 3. 월별 데이터 수집
# ==========================================

with requests.Session() as session:

    for month in tqdm(months, desc="STCIS 수집"):
        month_str = str(month)

        # 시작 월만 변경
        data["searchFromMonth"] = month_str

        # Form Data 생성
        form_data = list(data.items())
        form_data.extend(
            [("ddOption[]", value) for value in dd_options]
        )

        try:
            response = session.post(
                url,
                data=form_data,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            # JSON 파싱
            result = response.json()

            # 데이터 확인
            if not isinstance(result, dict):
                raise ValueError("JSON 응답이 딕셔너리가 아닙니다.")

            if "list" not in result:
                raise KeyError("응답에 list 키가 없습니다.")

            if not isinstance(result["list"], list):
                raise ValueError("list 값이 배열이 아닙니다.")

            df = pd.DataFrame(result["list"])

            # 수집 기준 월
            df["request_month"] = month_str

            # 결과 누적
            results.append(df)

            # 월별 CSV 저장
            file_path = output_dir / f"stcis_{month_str}.csv"

            df.to_csv(
                file_path,
                index=False,
                encoding="utf-8-sig"
            )

            tqdm.write(
                f"[완료] {month_str} | "
                f"{len(df):,}건 | "
                f"HTTP {response.status_code}"
            )

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            TypeError
        ) as e:

            failed_months.append(month_str)

            tqdm.write(
                f"[실패] {month_str} | {e}"
            )

        finally:
            # 서버 부하 방지
            time.sleep(random.uniform(3, 10))

# ==========================================
# 4. 전체 데이터 병합 및 저장
# ==========================================
import glob
results = [pd.read_csv(i) for i in glob.glob(f"{output_dir}/stcis_????-??.csv")]
if results:
    final_df = pd.concat(
        results,
        ignore_index=True
    )

    final_path = output_dir / "stcis_2026_all.csv"

    final_df.to_csv(
        final_path,
        index=False,
        encoding="utf-8-sig"
    )
