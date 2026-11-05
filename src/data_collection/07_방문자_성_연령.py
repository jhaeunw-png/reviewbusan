import os
import requests
import time
import pandas as pd
from tqdm import tqdm
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

# 부산 시군구 코드 목록 추출
station_df = pd.read_sql("select sido_cd, sgg_cd from districts", con=engine)
stations = station_df.loc[station_df["sido_cd"]=="26","sgg_cd"].unique()
stations = stations[~stations.isna()]
stations = stations.tolist()

url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "2",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_02_01_004",
    "dnname": "방문자 성연령별 분포",
}

# 수집할 데이터 기간(1990년 1월부터 지난달까지)
st_dt = pd.to_datetime("2018-01-01")
ed_dt = pd.Timestamp.now().strftime("%Y-%m-%d")
dates = pd.date_range(st_dt, ed_dt, freq="MS")

dfs = []
total = len(dates) * len(stations)
tasks = (
    (collect_date, station_id)
    for collect_date in dates
    for station_id in stations
)

error_dates = []
for collect_date, station_id in tqdm(tasks, total=total):
    try:
        # collect_date = pd.to_datetime("2018-01-01")
        start_date = collect_date.strftime("%Y%m")
        # end_date = (
        #     collect_date + pd.DateOffset(months=1)
        # ).strftime("%Y%m")
        
        form_data.update(
            {
                "SGG_CD":station_id,
                "BASE_YM1":start_date,
                "BASE_YM2":start_date,
                })
        time.sleep(.1)
        response = requests.post(
            url,
            data=form_data
        )
        data = response.json()
        df = pd.DataFrame(data["list"])
        df
        if df.shape[0]!=0:
            df = df.melt(
                id_vars=["AGEG_DIV_NM"],
                value_vars=["TOU_NUM1", "TOU_NUM2"],
                var_name="gender",
                value_name="tourist_cnt",
            )
            df["gender"] = df["gender"].map({
                "TOU_NUM1": "남성",
                "TOU_NUM2": "여성",
            })
            df["SGG_CD"] = station_id
            df["YEAR_MONTH"] = pd.to_datetime(start_date,format="%Y%m").strftime("%Y-%m")
            dfs.append(df)
        else:
            error_dates.append(start_date)
    except Exception as e:
        error_dates.append(start_date)

df = pd.concat(dfs, ignore_index=True)
sorted(df["YEAR_MONTH"].value_counts().index)
df.to_csv(
    "data/results/방문자_성_연령.csv",
    index=False,
    encoding="utf-8-sig",
)
