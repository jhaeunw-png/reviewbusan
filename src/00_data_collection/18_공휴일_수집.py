from pathlib import Path

import holidays
import pandas as pd


# 회귀분석에 사용하는 6개 국가·지역. 공휴일(대체공휴일 포함)만 수집한다.
COUNTRIES = {
    "KR": "한국",
    "JP": "일본",
    "CN": "중국",
    "US": "미국",
    "TW": "대만",
    "HK": "홍콩",
}
YEARS = range(2021, 2027)
OUTPUT_PATH = Path("sources/results/국가별_공휴일.csv")


rows = []
for country_code, country_name in COUNTRIES.items():
    calendar = holidays.country_holidays(country_code, years=YEARS, observed=True)
    for holiday_date, holiday_name in sorted(calendar.items()):
        rows.append({
            "country_code": country_code,
            "country_name": country_name,
            "holiday_date": holiday_date.isoformat(),
            "holiday_name": holiday_name,
        })

df = pd.DataFrame(rows)
if df.duplicated(["country_code", "holiday_date"]).any():
    raise ValueError("국가·날짜가 중복된 공휴일 데이터가 있습니다.")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
print(f"저장 행 수: {len(df):,}")
print(df.groupby("country_name").size().to_string())
