import pandas as pd


result_path = "data/results"

region_df = pd.read_csv(
    f"{result_path}/region_code.csv",
    dtype={"sido_cd": "string", "sgg_cd": "string", "umd_cd": "string"},
)
district_df = region_df[
    region_df["sido_cd"].eq("26")
    & region_df["sgg_cd"].notna()
    & region_df["umd_cd"].isna()
].copy()
district_df["sgg_nm"] = district_df["locatadd_nm"].str.replace(
    r"^부산광역시\s+", "", regex=True
)
district_df = district_df[["sgg_cd", "sgg_nm"]].drop_duplicates("sgg_cd")

paid_df = pd.read_csv(
    f"{result_path}/유료_관광지_내국인_입장객수.csv",
    usecols=["SGG_CD", "TAR_ID"],
    dtype={"SGG_CD": "string"},
).drop_duplicates()
paid_df = paid_df.rename(columns={"SGG_CD": "sgg_cd", "TAR_ID": "place_nm"})
paid_df["source_table"] = "paid_attractions"
paid_df["source_key"] = paid_df["sgg_cd"] + "|" + paid_df["place_nm"]
paid_df["place_type"] = "관광지"

navigation_files = {
    "인기관광지_네비_전체.csv": "관광지",
    "인기관광지_네비_외지인.csv": "관광지",
    "인기관광지_네비_현지인.csv": "관광지",
    "지역맛집_외지인.csv": "맛집",
    "지역맛집_현지인.csv": "맛집",
}
navigation_df = []

for file_name, place_type in navigation_files.items():
    df = pd.read_csv(
        f"{result_path}/{file_name}",
        usecols=["YEAR_MONTH", "SGG_CD", "MD5_POI_ID", "ITS_BRO_NM"],
        dtype={"SGG_CD": "string", "MD5_POI_ID": "string"},
    )
    df["place_type"] = place_type
    navigation_df.append(df)

place_df = pd.concat(navigation_df, ignore_index=True)
place_df = place_df.sort_values(["MD5_POI_ID", "YEAR_MONTH"]).drop_duplicates(
    "MD5_POI_ID", keep="last"
)
place_df = place_df.rename(
    columns={
        "MD5_POI_ID": "source_key",
        "SGG_CD": "sgg_cd",
        "ITS_BRO_NM": "place_nm",
    }
)
place_df["source_table"] = "tourism_places"

columns = ["source_table", "source_key", "place_type", "sgg_cd", "place_nm"]
result_df = pd.concat([paid_df[columns], place_df[columns]], ignore_index=True)
result_df = result_df.merge(district_df, on="sgg_cd", how="left", validate="many_to_one")
result_df = result_df[
    ["source_table", "source_key", "place_type", "sgg_cd", "sgg_nm", "place_nm"]
].sort_values(["source_table", "sgg_cd", "place_nm", "source_key"])

output_path = f"{result_path}/관광지_위치목록.csv"
result_df.to_csv(output_path, index=False, encoding="utf-8-sig")