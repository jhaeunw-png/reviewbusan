import os
import requests
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://apis.data.go.kr"

URL = f"{BASE_URL}/1741000/StanReginCd/getStanReginCdList"

## page_size: 한 페이지 당 자료 수
page_size = 100
params = {
    "serviceKey":API_KEY,
    "numberOfRows": page_size ,
    "pageNo": 1,
    "flag":"Y",
    "type":"json"
}
res = requests.get(URL, params= params)

selected_columns_dict = {
    "sido_cd":"시도코드",
    "sgg_cd":"시군구코드",
    "umd_cd":"읍면동코드",
    "region_cd":"전체지역코드",
    "locatadd_nm":"전체 주소명"
}
selected_columns = selected_columns_dict.keys()

dfs = list()
if res.status_code==200:
    data = res.json()
    try:
        if "StanReginCd" in data.keys():
            ## total_count: 총 자료 수
            ## total_page: 총 페이지 수
            total_count = int(data["StanReginCd"][0]["head"][0]["totalCount"])
        total_page = total_count//page_size + 1
        for page in tqdm(range(1, total_page + 1)):
            params.update({"pageNo":page})
            try:
                res = requests.get(URL, params= params)
                res.raise_for_status()
                data = res.json()
                station_df = pd.DataFrame(
                    data["StanReginCd"][1]["row"])
                dfs.append(station_df[selected_columns])
            except Exception as e:
                print(f"오류: {e}")
    except Exception as e:
        print(f"오류: {e}")
else:
    print(f"code {res.status_code}: 데이터 수집 실패")

df = pd.concat(dfs, ignore_index=True)
sido = df["sido_cd"].astype("string").str.zfill(2)
sgg = df["sgg_cd"].astype("string").str.zfill(3)
umd = df["umd_cd"].astype("string").str.zfill(3)

df["sido_cd"] = sido
# 시군구가 000이면 결측으로 둠
df["sgg_cd"] = (
    sido + sgg
).mask(sgg == "000")

# 시군구나 읍면동이 000이면 결측으로 둠
df["umd_cd"] = (
    sido + sgg + umd
).mask(
    (sgg == "000") | (umd == "000")
)

df["region_cd"] = (
    df["region_cd"]
    .astype("string")
    .str.zfill(10)
)

df.to_csv(
    "sources/results/region_code.csv",
    index=False,
    encoding="utf-8-sig",
)
