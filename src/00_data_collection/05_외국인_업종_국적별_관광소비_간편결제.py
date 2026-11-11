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

nationalities = {
    "대만": "158", "일본": "392", "독일": "276", "러시아": "643",
    "말레이시아": "458", "멕시코": "484", "몽골": "496", "미국": "840",
    "베트남": "704", "사우디아라비아": "682", "싱가포르": "702",
    "아랍에미리트": "784", "영국": "826", "인도": "356",
    "인도네시아": "360", "중국": "156", "카자흐스탄": "398",
    "캐나다": "124", "태국": "764", "튀르키예": "792", "프랑스": "250",
    "필리핀": "608", "호주": "036", "홍콩": "344",
}

url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"
form_data = {
    "SGG_CD2": "26410",
    "BASE_YM1": "202509",
    "BASE_YM2": "202608",
    "GEN_CD": "ALL",
    "srchAreaDate": "1",
    "touDivCd": "3",
    "tabDiv": "2",
    "localDvcdNm": "일본",
    "NAT_CD": "392",
    "qid": "LN_01_03_002_03",
}


# 수집할 데이터 기간(1990년 1월부터 지난달까지)
st_dt = pd.to_datetime("2018-01-01")
ed_dt = pd.Timestamp.now().strftime("%Y-%m-%d")
dates = pd.date_range(st_dt, ed_dt, freq="MS")

dfs = []
total = len(dates) * len(stations) * len(nationalities)
tasks = (
    (collect_date, station_id, nationality_nm, nat_cd)
    for collect_date in dates
    for station_id in stations
    for nationality_nm, nat_cd in nationalities.items()
)

error_dates = []
for collect_date, station_id, nationality_nm, nat_cd in tqdm(tasks, total=total):
    try:
        # collect_date = pd.to_datetime("2018-01-01")
        start_date = collect_date.strftime("%Y%m")
        # end_date = (
        #     collect_date + pd.DateOffset(months=1)
        # ).strftime("%Y%m")
        
        form_data.update(
            {
                "SGG_CD2":station_id,
                "BASE_YM1":start_date,
                "BASE_YM2":start_date,
                "localDvcdNm":nationality_nm,
                "NAT_CD":nat_cd,
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
            df["SGG_CD"] = station_id
            df["NAT_CD"] = nat_cd
            df["YEAR_MONTH"] = pd.to_datetime(start_date,format="%Y%m").strftime("%Y-%m")
            dfs.append(df)
        else:
            error_dates.append((start_date, station_id, nationality_nm))
    except Exception as e:
        error_dates.append((start_date, station_id, nationality_nm))

df = pd.concat(dfs, ignore_index=True)
sorted(df["YEAR_MONTH"].value_counts().index)
df.to_csv(
    "sources/results/외국인_업종_국적별_관광소비_및_방문.csv",
    index=False,
    encoding="utf-8-sig",
)
 
