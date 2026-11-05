import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv("./database/.env")

PORT = os.getenv("DB_PORT")
USER = os.getenv("MYSQL_USER")
DATABASE = os.getenv("MYSQL_DATABASE")
PW = os.getenv("MYSQL_PASSWORD")
HOST = os.getenv("HOST","localhost")

DB_INFO= f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DATABASE}"
engine = create_engine(DB_INFO,connect_args={})


query = "show tables"
with engine.connect() as con:
    result = con.execute(text(query))
    tables = result.fetchall()
tables

# 지역코드 데이터 저장
station_df = pd.read_csv(
    "data/results/region_code.csv",
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
sidos = station_df[["sido_cd", "address_nm"]].copy()
sidos["sido_nm"] = sidos["address_nm"].str.split().str[0]
sidos = sidos[["sido_cd", "sido_nm"]].drop_duplicates("sido_cd")
sidos.to_sql("sidos", con=engine, if_exists="append", index=False)

districts = station_df[
    station_df["sgg_cd"].notna() & station_df["umd_cd"].isna()
].copy()
districts["sgg_nm"] = districts["address_nm"].str.split().str[-1]
districts = districts[["sgg_cd", "sido_cd", "sgg_nm"]]
if (districts["sgg_cd"].str[:2] != districts["sido_cd"]).any():
    raise ValueError("시군구 코드와 시도 코드가 일치하지 않습니다.")
districts.to_sql("districts", con=engine, if_exists="append", index=False)

umds = station_df[station_df["umd_cd"].notna()].copy()
umds["umd_nm"] = umds["address_nm"].str.split().str[-1]
umds = umds[["region_cd", "umd_cd", "sgg_cd", "umd_nm"]]
if (umds["umd_cd"].str[:5] != umds["sgg_cd"]).any():
    raise ValueError("읍면동 코드와 시군구 코드가 일치하지 않습니다.")
if (umds["region_cd"].str[:8] != umds["umd_cd"]).any():
    raise ValueError("법정동 지역코드와 읍면동 코드가 일치하지 않습니다.")
umds.to_sql("umds", con=engine, if_exists="append", index=False, chunksize=5000)
