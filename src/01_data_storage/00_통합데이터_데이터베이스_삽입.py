import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv("./database/.env")

PORT = os.getenv("DB_PORT")
USER = os.getenv("MYSQL_USER")
DATABASE = os.getenv("MYSQL_DATABASE")
PW = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("HOST", "localhost")

DB_INFO = f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DB_INFO, connect_args={})


query = "show tables"
with engine.connect() as con:
    result = con.execute(text(query))
    tables = result.fetchall()
tables


# 국가 차원
nationality_source = pd.read_csv(
    "sources/results/국가별관광소비.csv",
    usecols=["DPTR_REGN_DTL_NM"],
).rename(columns={"DPTR_REGN_DTL_NM": "nationality_nm"})
foreign_nationality_source = pd.read_csv(
    "sources/results/외국인_업종_국적별_관광소비_및_방문.csv",
    usecols=["CUST_SIDO_NM", "NAT_CD"],
    dtype={"NAT_CD": "string"},
).rename(
    columns={
        "CUST_SIDO_NM": "nationality_nm",
        "NAT_CD": "nationality_cd",
    }
)
foreign_nationality_source["nationality_cd"] = (
    foreign_nationality_source["nationality_cd"].str.zfill(3)
)
foreign_nationality_source = foreign_nationality_source.drop_duplicates()
nationalities = nationality_source.drop_duplicates().merge(
    foreign_nationality_source,
    on="nationality_nm",
    how="left",
    validate="one_to_one",
)
nationalities = nationalities[["nationality_cd", "nationality_nm"]]
nationalities.to_sql(
    "nationalities",
    con=engine,
    if_exists="append",
    index=False,
)

# 국가별 공휴일
country_holidays = pd.read_csv("sources/results/국가별_공휴일.csv")
if country_holidays.duplicated(["country_code", "holiday_date"]).any():
    raise ValueError("국가별 공휴일에 중복된 국가·날짜가 있습니다.")
country_holidays["holiday_date"] = pd.to_datetime(
    country_holidays["holiday_date"], format="%Y-%m-%d"
).dt.date
country_holidays.to_sql(
    "country_holidays", con=engine, if_exists="append", index=False, chunksize=5000
)

nationality_keys = pd.read_sql(
    "SELECT nationality_id, nationality_nm FROM nationalities",
    con=engine,
)


# 국가별 외국인 방문객
df = pd.read_csv("sources/results/국가별외국인방문객현황.csv")
df = df.rename(
    columns={
        "REGN_NM": "nationality_nm",
        "TOU_NUM": "visitor_counts",
        "SGG_CD": "sgg_cd",
        "YEAR_MONTH": "base_ym",
    }
)
df["nationality_nm"] = df["nationality_nm"].replace(
    {"오스트레일리아": "호주"}
)
df = df.merge(nationality_keys, on="nationality_nm", how="left", validate="many_to_one")
if df["nationality_id"].isna().any():
    raise ValueError("국가 ID가 생성되지 않은 외국인 방문 데이터가 있습니다.")
df = df[["base_ym", "sgg_cd", "nationality_id", "visitor_counts"]]
df.to_sql(
    "nationality_visitor_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)

# 방문자 거주지
df = pd.read_csv("sources/results/방문자_거주지.csv")
df = df.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "DPTR_REGN_NM": "origin_region_nm",
        "DPTR_REGN_DTL_NM": "origin_detail_nm",
        "DTL_TOU_NUM": "visitor_counts",
    }
)
df = df[
    [
        "base_ym",
        "sgg_cd",
        "origin_region_nm",
        "origin_detail_nm",
        "visitor_counts",
    ]
]
df.to_sql(
    "residence_visitor_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 방문자 성별·연령
df = pd.read_csv("sources/results/방문자_성_연령.csv")
df = df.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "AGEG_DIV_NM": "age_group",
        "tourist_cnt": "visitor_counts",
    }
)
df = df[["base_ym", "sgg_cd", "age_group", "gender", "visitor_counts"]]
df.to_sql(
    "age_gender_visitor_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 방문자 유형별 방문자 수
df = pd.read_csv("sources/results/방문자_자료.csv", dtype={"BASE_DATE": "string"})
df = df.loc[df["TOU_DIV_NM"].isin(["현지인", "외지인", "외국인"])].copy()
df["base_ym"] = pd.to_datetime(df["BASE_DATE"], format="%Y%m").dt.strftime("%Y-%m")
df["sgg_nm"] = df["SIDO_NM"].str.replace(r"^부산광역시\s+", "", regex=True)
sgg_keys = pd.read_sql(
    "SELECT sgg_cd, sgg_nm FROM sigungu WHERE sido_cd = '26'", con=engine
)
df = df.merge(sgg_keys, on="sgg_nm", how="left", validate="many_to_one")
if df["sgg_cd"].isna().any():
    raise ValueError("시군구 코드가 없는 방문자 유형 데이터가 있습니다.")
df = df.rename(columns={"TOU_DIV_NM": "visitor_type", "TOU_NUM": "visitor_counts"})
df = df[["base_ym", "sgg_cd", "visitor_type", "visitor_counts"]]
df.to_sql(
    "visitor_type_counts", con=engine, if_exists="append", index=False, chunksize=5000
)


# 외지인 평균 체류시간·숙박방문자 비율
stay_sources = [
    ("체류시간.csv", "visitor_stay_times", "avg_stay_minutes"),
    ("숙박방문자_비율.csv", "stay_visitor_ratios", "stay_ratio_pct"),
]
for file_name, table_name, value_column in stay_sources:
    source_path = Path("sources/results") / file_name
    if not source_path.exists():
        print(f"미수집 파일 건너뜀: {source_path}")
        continue

    df = pd.read_csv(source_path, dtype={"SGG_CD": "string", "YEAR_MONTH": "string"})
    df = df.rename(columns={
        "SGG_CD": "sgg_cd",
        "YEAR_MONTH": "base_ym",
        "EXT_TOU_NUM": value_column,
    })[["base_ym", "sgg_cd", value_column]]
    df[value_column] = pd.to_numeric(df[value_column], errors="raise")
    if df.duplicated(["base_ym", "sgg_cd"]).any() or df.isna().any().any():
        raise ValueError(f"{file_name}에 중복 키 또는 결측값이 있습니다.")
    if (df[value_column] < 0).any() or (
        value_column == "stay_ratio_pct" and (df[value_column] > 100).any()
    ):
        raise ValueError(f"{file_name}에 범위를 벗어난 값이 있습니다.")
    df.to_sql(table_name, con=engine, if_exists="append", index=False, chunksize=5000)


# STCIS 월별 대중교통 이용 인원
# stcis_2026_all.csv는 월별 파일의 병합본이므로 제외한다.
transport_files = sorted(
    Path("sources/results/대중교통이용인원수집").glob("stcis_????-??.csv")
)
if not transport_files:
    raise FileNotFoundError("적재할 STCIS 월별 CSV가 없습니다.")

transport_frames = []
for source_path in transport_files:
    df = pd.read_csv(
        source_path,
        dtype={"yyyymm": "string", "sggCd": "string", "userTypeCd": "string"},
    )
    file_month = source_path.stem.removeprefix("stcis_")
    if not df["yyyymm"].eq(file_month.replace("-", "")).all():
        raise ValueError(f"파일명과 기준 월이 다릅니다: {source_path}")
    transport_frames.append(df[
        ["yyyymm", "sggCd", "userTypeCd", "userTypeNm", "useStf"]
    ])

df = pd.concat(transport_frames, ignore_index=True).rename(columns={
    "sggCd": "sgg_cd",
    "userTypeCd": "user_type_cd",
    "userTypeNm": "user_type_nm",
    "useStf": "use_cnt",
})
df["base_ym"] = pd.to_datetime(df.pop("yyyymm"), format="%Y%m").dt.strftime("%Y-%m")
df["user_type_cd"] = df["user_type_cd"].str.zfill(2)
df["use_cnt"] = pd.to_numeric(df["use_cnt"], errors="raise")
df = df[["base_ym", "sgg_cd", "user_type_cd", "user_type_nm", "use_cnt"]]
if df.isna().any().any() or df.duplicated(
    ["base_ym", "sgg_cd", "user_type_cd"]
).any():
    raise ValueError("STCIS 데이터에 결측값 또는 중복 키가 있습니다.")
if (df["use_cnt"] < 0).any() or (df["use_cnt"] % 1 != 0).any():
    raise ValueError("STCIS 이용 인원에 음수 또는 소수가 있습니다.")
df["use_cnt"] = df["use_cnt"].astype("int64")
df.to_sql(
    "public_transport_counts", con=engine, if_exists="append", index=False, chunksize=5000
)


# 국가별 관광소비
df = pd.read_csv("sources/results/국가별관광소비.csv")
df = df.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "DPTR_REGN_DTL_NM": "nationality_nm",
        "DTL_TOU_NUM": "spend_amt",
    }
)
df = df.merge(nationality_keys, on="nationality_nm", how="left", validate="many_to_one")
if df["nationality_id"].isna().any():
    raise ValueError("국가 ID가 생성되지 않은 관광소비 데이터가 있습니다.")
df = df[["base_ym", "sgg_cd", "nationality_id", "spend_amt"]]
df.to_sql(
    "nationality_amounts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 관광 대업종 차원
industry_source = pd.read_csv(
    "sources/results/업종별관광소비.csv",
    usecols=["DPTR_REGN_NM"],
)
foreign_industry_source = pd.read_csv(
    "sources/results/외국인_업종_국적별_관광소비_및_방문.csv",
    usecols=["DPTR_REGN_NM"],
)
industries = pd.concat(
    [industry_source, foreign_industry_source],
    ignore_index=True,
)
industries = industries.rename(columns={"DPTR_REGN_NM": "industry_nm"})
industries = industries.drop_duplicates()
industries.to_sql(
    "tourism_categories",
    con=engine,
    if_exists="append",
    index=False,
)

industry_keys = pd.read_sql(
    "SELECT industry_id, industry_nm FROM tourism_categories",
    con=engine,
)


# 업종별 관광소비
df = pd.read_csv("sources/results/업종별관광소비.csv")
df = df.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "DPTR_REGN_NM": "industry_nm",
        "TOU_NUM": "spend_amt",
    }
)
df = df.merge(industry_keys, on="industry_nm", how="left", validate="many_to_one")
if df["industry_id"].isna().any():
    raise ValueError("대업종 ID가 생성되지 않은 관광소비 데이터가 있습니다.")
df = df[["base_ym", "sgg_cd", "industry_id", "spend_amt"]]
df.to_sql(
    "tourism_category_amounts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 외국인 국가·업종별 간편결제 관광소비
df = pd.read_csv(
    "sources/results/외국인_업종_국적별_관광소비_및_방문.csv",
    dtype={"SGG_CD": "string", "NAT_CD": "string"},
)
df = df.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "NAT_CD": "nationality_cd",
        "CUST_SIDO_NM": "nationality_nm",
        "DPTR_REGN_NM": "industry_nm",
        "DPTR_REGN_DTL_NM": "detail_industry_nm",
        "DTL_TOU_NUM": "spend_amt",
    }
)
df = df[
    [
        "base_ym",
        "sgg_cd",
        "nationality_nm",
        "industry_nm",
        "detail_industry_nm",
        "spend_amt",
    ]
]
df["spend_amt"] = df["spend_amt"].round().astype("int64")

if df.duplicated(
    [
        "base_ym",
        "sgg_cd",
        "nationality_nm",
        "industry_nm",
        "detail_industry_nm",
    ]
).any():
    raise ValueError("외국인 국가·업종별 간편결제 데이터에 중복 키가 있습니다.")

df = df.merge(nationality_keys, on="nationality_nm", how="left", validate="many_to_one")
if df["nationality_id"].isna().any():
    raise ValueError("국가 ID가 생성되지 않은 간편결제 데이터가 있습니다.")

detail_industries = df[
    ["industry_nm", "detail_industry_nm"]
].drop_duplicates()
detail_industries = detail_industries.merge(
    industry_keys,
    on="industry_nm",
    how="left",
    validate="many_to_one",
)
if detail_industries["industry_id"].isna().any():
    raise ValueError("대업종 ID가 생성되지 않은 세부업종이 있습니다.")
detail_industries = detail_industries[
    ["industry_id", "detail_industry_nm"]
]
detail_industries.to_sql(
    "tourism_detail_categories",
    con=engine,
    if_exists="append",
    index=False,
)

detail_industry_keys = pd.read_sql(
    """
    SELECT
        d.detail_industry_id,
        d.detail_industry_nm,
        i.industry_nm
    FROM tourism_detail_categories d
    JOIN tourism_categories i
        ON d.industry_id = i.industry_id
    """,
    con=engine,
)
df = df.merge(
    detail_industry_keys,
    on=["industry_nm", "detail_industry_nm"],
    how="left",
    validate="many_to_one",
)
if df["detail_industry_id"].isna().any():
    raise ValueError("세부업종 ID가 생성되지 않은 소비 데이터가 있습니다.")

df = df[
    [
        "base_ym",
        "sgg_cd",
        "nationality_id",
        "detail_industry_id",
        "spend_amt",
    ]
]
df.to_sql(
    "foreign_epay_amounts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 유료 관광지
paid_counts = pd.read_csv(
    "sources/results/유료_관광지_내국인_입장객수.csv",
    dtype={"SGG_CD": "string"},
)
paid_counts = paid_counts.rename(
    columns={
        "YEAR_MONTH": "base_ym",
        "SGG_CD": "sgg_cd",
        "TAR_ID": "attraction_nm",
        "RK": "ranking",
        "NATI_TOU_NUM": "domestic_cnt",
        "TOTAL_NUM": "total_cnt",
    }
)

paid_attractions = paid_counts[
    ["sgg_cd", "attraction_nm"]
].drop_duplicates()
paid_attractions.to_sql(
    "paid_attractions",
    con=engine,
    if_exists="append",
    index=False,
)

paid_attraction_keys = pd.read_sql(
    """
    SELECT attraction_id, sgg_cd, attraction_nm
    FROM paid_attractions
    """,
    con=engine,
)
paid_attraction_keys["sgg_cd"] = paid_attraction_keys["sgg_cd"].astype("string")
paid_counts = paid_counts.merge(
    paid_attraction_keys,
    on=["sgg_cd", "attraction_nm"],
    how="left",
    validate="many_to_one",
)
if paid_counts["attraction_id"].isna().any():
    raise ValueError("대체키가 생성되지 않은 유료 관광지가 있습니다.")

paid_counts = paid_counts[
    [
        "base_ym",
        "sgg_cd",
        "attraction_id",
        "ranking",
        "domestic_cnt",
        "total_cnt",
    ]
]
paid_counts.to_sql(
    "paid_attraction_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 내비게이션 검색
# 인기관광지_네비.csv는 인기관광지_네비_전체.csv와 중복되어 제외
navigation_files = [
    (
        "인기관광지_네비_전체.csv",
        "관광지",
        "전체",
        "KTO_CATE_NAME_B",
        "SRCH_CNT",
    ),
    (
        "인기관광지_네비_외지인.csv",
        "관광지",
        "외지인",
        "KTO_CATE_NAME_B",
        "SRCH_CNT",
    ),
    (
        "인기관광지_네비_현지인.csv",
        "관광지",
        "현지인",
        "KTO_CATE_NAME_B",
        "SRCH_NTV_CNT",
    ),
    (
        "지역맛집_외지인.csv",
        "맛집",
        "외지인",
        "KTO_CATE_NAME_C",
        "SRCH_CNT",
    ),
    (
        "지역맛집_현지인.csv",
        "맛집",
        "현지인",
        "KTO_CATE_NAME_C",
        "SRCH_NTV_CNT",
    ),
]

place_frames = []
navigation_count_frames = []

for file_name, poi_type, audience_type, category_column, count_column in navigation_files:
    df = pd.read_csv(f"sources/results/{file_name}")
    df = df.rename(
        columns={
            "YEAR_MONTH": "base_ym",
            "SGG_CD": "sgg_cd",
            "MD5_POI_ID": "poi_id",
            "ITS_BRO_ID": "source_poi_id",
            "ITS_BRO_NM": "poi_nm",
            category_column: "category_nm",
            "RK": "ranking",
            count_column: "search_cnt",
        }
    )
    df["place_type"] = poi_type
    df["audience_type"] = audience_type
    place_frames.append(
        df[
            [
                "base_ym",
                "poi_id",
                "source_poi_id",
                "sgg_cd",
                "place_type",
                "poi_nm",
                "category_nm",
            ]
        ].rename(columns={"poi_nm": "place_nm"})
    )
    navigation_count_frames.append(
        df[
            [
                "base_ym",
                "sgg_cd",
                "poi_id",
                "audience_type",
                "ranking",
                "search_cnt",
            ]
        ]
    )

df = pd.concat(place_frames, ignore_index=True)
df = df.drop_duplicates(["base_ym", "poi_id"])
df = df.sort_values(["poi_id", "base_ym"])
df = df.drop_duplicates("poi_id", keep="last")
df = df.drop(columns="base_ym")

location_df = pd.read_csv(
    "sources/results/관광지_위치목록_완료.csv",
    usecols=[
        "source_table",
        "source_key",
        "latitude",
        "longitude",
        "search_status",
    ],
    dtype={"source_key": "string"},
)
location_df = location_df[
    location_df["source_table"].eq("tourism_places")
    & location_df["search_status"].isin(["matched", "district_center"])
    & location_df["latitude"].notna()
    & location_df["longitude"].notna()
]
location_df = location_df.rename(columns={"source_key": "poi_id"})
location_df = location_df[["poi_id", "latitude", "longitude"]]

df = df.merge(location_df, on="poi_id", how="left", validate="one_to_one")
df.to_sql(
    "tourism_places",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)

df = pd.concat(navigation_count_frames, ignore_index=True)
df = df[
    [
        "base_ym",
        "sgg_cd",
        "poi_id",
        "audience_type",
        "ranking",
        "search_cnt",
    ]
]
df.to_sql(
    "navigation_search_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 관심 관광지 5개 파일 통합
category_frames = []
interest_frames = []

interest_files = [
    ("관심_관광지_내국인.csv", "내국인", "SUM_VISITR_NUM"),
    ("관심_관광지_영어권.csv", "영어권", "SUM_USER_VST_CNT"),
    ("관심_관광지_일어권.csv", "일본어", "SUM_USER_VST_CNT"),
    ("관심_관광지_중간체.csv", "중간체", "SUM_USER_VST_CNT"),
    ("관심_관광지_중번체.csv", "중번체", "SUM_USER_VST_CNT"),
]

for file_name, language, count_column in interest_files:
    raw_df = pd.read_csv(
        f"sources/results/{file_name}",
        keep_default_na=False,
        na_values=[""],
    )
    category_frames.append(raw_df)

    df = raw_df.rename(
        columns={
            "YEAR_MONTH": "base_ym",
            "SGG_CD": "sgg_cd",
            "CONT_ID": "content_id",
            "TAR_NM": "content_nm",
            "URL": "content_url",
            "KTO_CATE_SCLS_CD": "small_cat_cd",
            count_column: "visitor_counts",
        }
    )
    df["language"] = language
    df = df[
        [
            "base_ym",
            "sgg_cd",
            "content_id",
            "language",
            "content_nm",
            "content_url",
            "small_cat_cd",
            "visitor_counts",
        ]
    ]
    interest_frames.append(df)

category_df = pd.concat(category_frames, ignore_index=True)
category_df = category_df.rename(
    columns={
        "KTO_CATE_SCLS_CD": "small_cat_cd",
        "KTO_CATE_SCLS_NM": "small_cat_nm",
        "KTO_CATE_MCLS_CD": "mid_cat_cd",
        "KTO_CATE_MCLS_NM": "mid_cat_nm",
        "KTO_CATE_LCLS_CD": "large_cat_cd",
        "KTO_CATE_LCLS_NM": "large_cat_nm",
    }
)

large_categories = category_df[
    ["large_cat_cd", "large_cat_nm"]
].drop_duplicates(["large_cat_cd", "large_cat_nm"])
large_categories.to_sql(
    "kto_large_categories",
    con=engine,
    if_exists="append",
    index=False,
)

mid_categories = category_df[
    ["mid_cat_cd", "mid_cat_nm", "large_cat_cd"]
].drop_duplicates("mid_cat_cd")
mid_categories.to_sql(
    "kto_mid_categories",
    con=engine,
    if_exists="append",
    index=False,
)

small_categories = category_df[
    ["small_cat_cd", "small_cat_nm", "mid_cat_cd"]
].drop_duplicates("small_cat_cd")
small_categories.to_sql(
    "kto_small_categories",
    con=engine,
    if_exists="append",
    index=False,
)

df = pd.concat(interest_frames, ignore_index=True)

# 콘텐츠별·언어권별 명칭과 URL은 가장 최근 연월 값을 대표값으로 사용한다.
content_localizations = (
    df.sort_values("base_ym")
    .drop_duplicates(["content_id", "language"], keep="last")
    [["content_id", "language", "content_nm", "content_url"]]
)

# 좌표 검색용 대표명은 내국인 최신 명칭을 우선하고, 없으면 다른 언어권
# 최신 명칭을 사용한다. 동일 content_id가 복수 구군·소분류에 연결되는
# 사례가 있으므로 구군과 소분류는 관광 콘텐츠 본체에 저장하지 않는다.
language_priority = {
    "내국인": 0,
    "영어권": 1,
    "일본어": 2,
    "중간체": 3,
    "중번체": 4,
}
tourism_contents = content_localizations.copy()
tourism_contents["language_priority"] = tourism_contents["language"].map(
    language_priority
)
tourism_contents = (
    tourism_contents.sort_values(["content_id", "language_priority"])
    .drop_duplicates("content_id", keep="first")
    [["content_id", "content_nm"]]
)

# 위경도 수집용 관광지 목록도 함께 생성한다. 동일 content_id가 복수
# 구군에 연결되는 경우 검색 보조값으로 가장 최근 연월의 구군 코드를 쓴다.
latest_content_regions = (
    df.sort_values("base_ym")
    .drop_duplicates("content_id", keep="last")
    [["content_id", "sgg_cd"]]
)
interest_location_list = tourism_contents.merge(
    latest_content_regions,
    on="content_id",
    how="left",
    validate="one_to_one",
)
interest_location_list["search_query"] = (
    "부산광역시 " + interest_location_list["content_nm"].astype("string")
)
interest_location_list["latitude"] = pd.Series(
    "", index=interest_location_list.index, dtype="string"
)
interest_location_list["longitude"] = pd.Series(
    "", index=interest_location_list.index, dtype="string"
)
interest_location_list["search_status"] = pd.Series(
    "미수집", index=interest_location_list.index, dtype="string"
)
interest_location_list.to_csv(
    "sources/results/관심_관광지_위치목록.csv",
    index=False,
    encoding="utf-8-sig",
)
print("저장 완료: sources/results/관심_관광지_위치목록.csv")

interest_locations = pd.read_csv(
    "sources/results/관심_관광지_위치목록_완료.csv",
    usecols=["content_id", "latitude", "longitude", "search_status"],
)
interest_locations = interest_locations[
    interest_locations["search_status"].isin(
        ["matched_sgg", "matched_busan", "district_center"]
    )
    & interest_locations["latitude"].notna()
    & interest_locations["longitude"].notna()
]
interest_locations = interest_locations[["content_id", "latitude", "longitude"]]
tourism_contents = tourism_contents.merge(
    interest_locations, on="content_id", how="left", validate="one_to_one"
)

tourism_contents.to_sql(
    "tourism_contents",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)

content_localizations.to_sql(
    "tourism_content_localizations",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)

df = df.drop_duplicates(
    ["base_ym", "sgg_cd", "content_id", "language"]
)
df = df[
    [
        "base_ym",
        "sgg_cd",
        "content_id",
        "language",
        "small_cat_cd",
        "visitor_counts",
    ]
]
df.to_sql(
    "tourism_interest_counts",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)


# 부산 숙박업소·일반음식점
sgg_code_by_name = sgg_keys.set_index("sgg_nm")["sgg_cd"]


def load_businesses(file_name, table_name, source_type=None):
    source_path = Path("sources/downloads") / file_name
    row_no = 1
    for raw_df in pd.read_csv(source_path, encoding="cp949", chunksize=2000):
        raw_df = raw_df.reset_index(drop=True)
        road_district = raw_df["도로명주소"].str.extract(
            r"^부산광역시\s+([^\s]+)"
        )[0]
        lot_district = raw_df["지번주소"].str.extract(
            r"^부산광역시\s+([^\s]+)"
        )[0]
        district = road_district.where(
            road_district.isin(sgg_code_by_name.index), lot_district
        )
        raw_records = raw_df.astype(object).where(pd.notna(raw_df), None).to_dict(
            "records"
        )

        result = pd.DataFrame({
            "source_row_no": range(row_no, row_no + len(raw_df)),
            "license_no": raw_df["관리번호"],
            "business_nm": raw_df["사업장명"],
            "status_nm": raw_df["영업상태명"],
            "license_date": pd.to_datetime(
                raw_df["인허가일자"], errors="coerce"
            ).dt.date,
            "closure_date": pd.to_datetime(
                raw_df["폐업일자"], errors="coerce"
            ).dt.date,
            "road_address": raw_df["도로명주소"],
            "lot_address": raw_df["지번주소"],
            "sgg_cd": district.map(sgg_code_by_name),
            "source_x": pd.to_numeric(raw_df["좌표정보(X)"], errors="coerce"),
            "source_y": pd.to_numeric(raw_df["좌표정보(Y)"], errors="coerce"),
            "source_modified_at": pd.to_datetime(
                raw_df["최종수정시점"], errors="coerce"
            ),
            "source_data": [
                json.dumps(record, ensure_ascii=False, default=str)
                for record in raw_records
            ],
        })

        if table_name == "stays":
            result["source_type"] = source_type
            result["business_subtype"] = raw_df[
                "관광숙박업상세명" if source_type == "tourist_lodging" else "업태구분명"
            ]
            if source_type == "tourist_lodging":
                result["room_cnt"] = pd.to_numeric(
                    raw_df["객실수"], errors="coerce"
                )
            else:
                result["room_cnt"] = pd.concat(
                    [
                        pd.to_numeric(raw_df["양실수"], errors="coerce"),
                        pd.to_numeric(raw_df["한실수"], errors="coerce"),
                    ],
                    axis=1,
                ).sum(axis=1, min_count=1)
        else:
            result["business_subtype"] = raw_df["업태구분명"]
            result["facility_area_sqm"] = pd.to_numeric(
                raw_df["시설총규모"].astype("string").str.replace(",", "", regex=False),
                errors="coerce",
            )

        result.to_sql(
            table_name, con=engine, if_exists="append", index=False, chunksize=1000
        )
        row_no += len(raw_df)
    print(f"{table_name} 저장 행 수: {row_no - 1:,}")


load_businesses("문화_관광숙박업_부산광역시.csv", "stays", "tourist_lodging")
load_businesses("문화_숙박업_부산광역시.csv", "stays", "lodging")
load_businesses("식품_일반음식점_부산광역시.csv", "restaurants")


# MICE 행사
df = pd.read_csv("sources/results/MICE관련행사정보.csv")
dates = df["evntYmd"].str.split("~", n=1, expand=True)
df["start_date"] = pd.to_datetime(
    dates[0].str.replace("-", "").str.strip(),
    format="%Y%m%d",
).dt.date

df["end_date"] = pd.to_datetime(
    dates[1].str.replace("-", "").str.strip(),
    format="%Y%m%d",
).dt.date

wrong_date = df["start_date"] > df["end_date"]

df.loc[wrong_date, ["start_date", "end_date"]] = (
    df.loc[wrong_date, ["end_date", "start_date"]].to_numpy()
)

df = df.rename(
    columns={
        "idx": "event_id",
        "YEAR_MONTH": "base_ym",
        "evntSeClass": "event_type_cd",
        "evntSeTxt": "event_type_nm",
        "evntNm": "event_nm",
        "evntPlcNm": "place_nm",
        "evntTmCn": "event_time",
        "atchFileId": "attachment_id",
        "fileSn": "file_sn",
    }
)
df = df[
    [
        "event_id",
        "base_ym",
        "event_type_cd",
        "event_type_nm",
        "event_nm",
        "place_nm",
        "start_date",
        "end_date",
        "event_time",
        "attachment_id",
        "file_sn",
    ]
]
df.to_sql(
    "mice_events",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=5000,
)
