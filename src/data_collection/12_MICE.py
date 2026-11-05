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

# 부산 MICE 플랫폼
# https://www.busanmice.or.kr/portal/evntInfo/list.do?mid=0203000000&token=1790413534007
url = "https://www.busanmice.or.kr/portal/evntInfo/list/data.do"
LINK_INST_CD = ",".join([
    "evntInfoBusan",
    "evntInfoBto",
    "evntInfoBexco",
    "evntInfoBpex",
    "evntInfoBipa",
])

form_data =  {
        "searchSdt": "",
        "searchEdt": "",
        "searchYr": 2026,
        "searchMm": "08",
        "searchTxt": "",
        "linkInstCd": LINK_INST_CD,
        "mode": "list",
        "listEvntSeCd": "",
        "listPage": 1,
    }


# 수집할 데이터 기간(1990년 1월부터 지난달까지)
st_dt = pd.to_datetime("2023-01-01")
ed_dt = pd.Timestamp.now().strftime("%Y-%m-%d")
dates = pd.date_range(st_dt, ed_dt, freq="MS")

dfs = []
error_dates = []
for collect_date in tqdm(dates):
    try:
        # collect_date = pd.to_datetime("2018-01-01")
        year = collect_date.strftime("%Y")
        month = collect_date.strftime("%m")   
        start_date = collect_date.strftime("%Y%m")
        form_data.update(
            {
                "searchYr":year,
                "searchMm":month,
                })
        time.sleep(.1)
        response = requests.post(
            url,
            data=form_data,
                verify=False,
        )
        data = response.json()
        total_cnt = data["totalCnt"]
        
        for page in range(1, total_cnt//12 + 2):
            form_data.update(
                {
                    "searchYr":year,
                    "searchMm":month,
                    "listPage":page,
                    })
            time.sleep(.1)
            response = requests.post(
                url,
                data=form_data,
                    verify=False,
            )
            data = response.json()
            df = pd.DataFrame(data["dataList"])
            if df.shape[0]!=0:
                df["YEAR_MONTH"] = pd.to_datetime(start_date,format="%Y%m").strftime("%Y-%m")
                dfs.append(df)
        else:
            error_dates.append(start_date)
    except Exception as e:
        error_dates.append(start_date)

df = pd.concat(dfs, ignore_index=True)
sorted(df["YEAR_MONTH"].value_counts().index)
df.to_csv(
    "data/results/MICE관련행사정보.csv",
    index=False,
    encoding="utf-8-sig",
)
