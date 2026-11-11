import os
from pathlib import Path
import geopandas as gpd
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv("./database/.env")

PORT = os.getenv("DB_PORT")
USER = os.getenv("MYSQL_USER")
DATABASE = os.getenv("MYSQL_DATABASE")
PW = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("HOST","localhost")

DB_INFO= f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DB_INFO,connect_args={})


def load_region_areas():
    """10자리 법정동 경계에서 시도·시군구·법정동 면적(km²)을 계산한다."""
    boundary_path = Path(os.getenv("REGION_BOUNDARY_PATH", "sources/downloads/bjd.shp"))
    code_column = os.getenv("REGION_BOUNDARY_CODE_COLUMN", "BJD_CD")
    if not boundary_path.is_file():
        raise FileNotFoundError(
            f"법정동 경계 파일이 없습니다: {boundary_path}. "
            "REGION_BOUNDARY_PATH에 10자리 법정동 경계 파일 경로를 지정하세요."
        )

    boundaries = gpd.read_file(boundary_path)
    if code_column not in boundaries.columns:
        raise ValueError(f"경계 파일에 코드 컬럼 {code_column!r}이 없습니다.")
    if boundaries.crs is None:
        raise ValueError("경계 파일에 CRS가 없습니다. 원본 좌표계를 확인해 지정하세요.")

    boundaries = boundaries[[code_column, "geometry"]].copy()
    boundaries["region_cd"] = boundaries[code_column].astype("string").str.strip()
    if not boundaries["region_cd"].str.fullmatch(r"\d{10}").fillna(False).all():
        raise ValueError("경계 코드는 법정동·법정리의 10자리 region_cd여야 합니다.")
    if boundaries.geometry.isna().any() or boundaries.geometry.is_empty.any():
        raise ValueError("경계 파일에 비어 있는 도형이 있습니다.")

    # EPSG:5179의 좌표 단위는 미터이므로 면적을 1,000,000으로 나눈다.
    regions = boundaries.to_crs("EPSG:5179").dissolve(by="region_cd")
    regions["area_km2"] = regions.geometry.area / 1_000_000
    if (regions["area_km2"] <= 0).any():
        raise ValueError("면적이 0 이하인 법정동 경계가 있습니다.")

    umd_areas = regions[["area_km2"]].reset_index()
    umd_areas["sgg_cd"] = umd_areas["region_cd"].str[:5]
    umd_areas["sido_cd"] = umd_areas["region_cd"].str[:2]
    sigungu_areas = umd_areas.groupby("sgg_cd", as_index=False)["area_km2"].sum()
    sido_areas = umd_areas.groupby("sido_cd", as_index=False)["area_km2"].sum()
    return sido_areas, sigungu_areas, umd_areas[["region_cd", "area_km2"]]


def require_areas(frame, code_column, label):
    missing = frame.loc[frame["area_km2"].isna(), code_column]
    if not missing.empty:
        sample = ", ".join(missing.head(5).astype(str))
        raise ValueError(f"{label} 경계 면적이 없는 코드 {len(missing)}개: {sample}")
    frame["area_km2"] = frame["area_km2"].round(6)
    return frame

# 지역코드 데이터 저장
station_df = pd.read_csv(
    "sources/results/region_code.csv",
    dtype={
        "region_cd": "string",
        "sido_cd": "string",
        "sgg_cd": "string",
        "umd_cd": "string",
    },
)
station_df.rename(
    columns={"locatadd_nm": "address_nm"},
    inplace=True,
)
sido_areas, sigungu_areas, umd_areas = load_region_areas()

sidos = station_df[["sido_cd", "address_nm"]].copy()
sidos["sido_nm"] = sidos["address_nm"].str.split().str[0]
sidos = sidos[["sido_cd", "sido_nm"]].drop_duplicates("sido_cd")
sidos = require_areas(
    sidos.merge(sido_areas, on="sido_cd", how="left", validate="one_to_one"),
    "sido_cd", "시도",
)

sigungu = station_df[
    station_df["sgg_cd"].notna() & station_df["umd_cd"].isna()
].copy()
sigungu["sgg_nm"] = sigungu["address_nm"].str.split().str[-1]
sigungu = sigungu[["sgg_cd", "sido_cd", "sgg_nm"]]
sigungu = require_areas(
    sigungu.merge(sigungu_areas, on="sgg_cd", how="left", validate="one_to_one"),
    "sgg_cd", "시군구",
)
if (sigungu["sgg_cd"].str[:2] != sigungu["sido_cd"]).any():
    raise ValueError("시군구 코드와 시도 코드가 일치하지 않습니다.")

umds = station_df[station_df["umd_cd"].notna()].copy()
umds["umd_nm"] = umds["address_nm"].str.split().str[-1]
umds = umds[["region_cd", "umd_cd", "sgg_cd", "umd_nm"]]
umds = require_areas(
    umds.merge(umd_areas, on="region_cd", how="left", validate="one_to_one"),
    "region_cd", "읍면동·법정리",
)
if (umds["umd_cd"].str[:5] != umds["sgg_cd"]).any():
    raise ValueError("읍면동 코드와 시군구 코드가 일치하지 않습니다.")
if (umds["region_cd"].str[:8] != umds["umd_cd"]).any():
    raise ValueError("법정동 지역코드와 읍면동 코드가 일치하지 않습니다.")

with engine.begin() as connection:
    sidos.to_sql("sidos", con=connection, if_exists="append", index=False)
    sigungu.to_sql("sigungu", con=connection, if_exists="append", index=False)
    umds.to_sql("umds", con=connection, if_exists="append", index=False, chunksize=5000)
