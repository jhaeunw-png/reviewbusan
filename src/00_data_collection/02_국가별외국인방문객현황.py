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
station_df = pd.read_sql("select sido_cd, sgg_cd from sigungu", con=engine)
stations = station_df.loc[station_df["sido_cd"]=="26","sgg_cd"].unique()
stations = stations[~stations.isna()]
stations = stations.tolist()

url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202607",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDIV": "1",
    "sggIntgYnFlag": "N",
    "qid": "LN_10_01_002",
    "dnname": "국가별 외국인 방문 현황",
}

# DPTR_REGN_NM: 출발지역명
# DPTR_REGN_DTL_NM: 출발지역 상세명
# DTL_TOU_NUM: 상세 관광객 수
# DTL_TOU_NUM_SQRT: 관광객 수 제곱근
# TOT_DPTR_REGN_NM_RATE: 전체 출발지역 대비 비율

# 수집할 데이터 기간(2019년 1월부터 지난달까지)
st_dt = pd.to_datetime("2019-01-01")
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
        start_date = collect_date.strftime("%Y%m")
        # end_date = (
        #     collect_date + pd.DateOffset(months=1)
        # ).strftime("%Y%m")
        
        form_data.update(
            {"SGG_CD":station_id,
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
        # df
        if df.shape[0]!=0:
            df = df[["DPTR_REGN_DTL_NM", "DTL_TOU_NUM"]]
            df.columns = ["REGN_NM", "TOU_NUM"]
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
    "sources/results/국가별외국인방문객현황.csv",
    index=False,
    encoding="utf-8-sig",
)
