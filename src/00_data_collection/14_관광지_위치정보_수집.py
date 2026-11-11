import os
import time

import geopandas as gpd
import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv(".env", override=True)
kakao_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()

if not kakao_api_key:
    raise ValueError(".env에 KAKAO_REST_API_KEY를 입력하세요.")

input_path = "sources/results/관광지_위치목록.csv"
output_path = "sources/results/관광지_위치목록_완료.csv"
location_columns = [
    "search_query",
    "kakao_place_id",
    "kakao_place_nm",
    "category_nm",
    "address_nm",
    "road_address_nm",
    "longitude",
    "latitude",
    "search_status",
]

# 카카오 검색 실패 시 사용할 부산 구·군 중심점 좌표를 계산한다.
district_map = gpd.read_file("data/지적도/sig.shp")
district_map["SIG_CD"] = district_map["SIG_CD"].astype(str).str.zfill(5)
district_map = district_map[district_map["SIG_CD"].str.startswith("26")].copy()

if district_map.crs is None:
    # 이 지적도는 함께 제공된 GRS80_UTMK.prj 기준 EPSG:5179이다.
    district_map = district_map.set_crs("EPSG:5179")

district_centers = district_map.to_crs("EPSG:5179")
district_centers["geometry"] = district_centers.geometry.centroid
district_centers = district_centers.to_crs("EPSG:4326")
district_center_coordinates = {
    row["SIG_CD"]: (row.geometry.x, row.geometry.y)
    for _, row in district_centers.iterrows()
}

if os.path.exists(output_path):
    result_df = pd.read_csv(
        output_path,
        dtype={"source_key": "string", "sgg_cd": "string", "kakao_place_id": "string"},
    )
else:
    result_df = pd.read_csv(
        input_path,
        dtype={"source_key": "string", "sgg_cd": "string"},
    )
    result_df[location_columns] = pd.NA

result_df[location_columns] = result_df[location_columns].astype("string")

headers = {"Authorization": f"KakaoAK {kakao_api_key}"}
search_status = result_df["search_status"].fillna("").str.strip()
search_df = result_df[search_status.isin(["", "not_found"])]

for count, (index, row) in enumerate(search_df.iterrows(), 1):
    query = f"부산광역시 {row['sgg_nm']} {row['place_nm']}"

    try:
        response = requests.get(
            "https://dapi.kakao.com/v2/local/search/keyword.json",
            headers=headers,
            params={"query": query, "size": 15},
            timeout=10,
        )
        response.raise_for_status()
    except requests.HTTPError as error:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        raise RuntimeError(
            f"Kakao API 오류 ({response.status_code}): {response.text}"
        ) from error
    except requests.RequestException:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        raise

    documents = response.json()["documents"]
    matches = [
        place
        for place in documents
        if f"부산 {row['sgg_nm']}" in f"{place['address_name']} {place['road_address_name']}"
    ]

    result_df.at[index, "search_query"] = query

    if matches:
        place = matches[0]
        result_df.loc[
            index,
            [
                "kakao_place_id",
                "kakao_place_nm",
                "category_nm",
                "address_nm",
                "road_address_nm",
                "longitude",
                "latitude",
                "search_status",
            ],
        ] = [
            place["id"],
            place["place_name"],
            place["category_name"],
            place["address_name"],
            place["road_address_name"],
            place["x"],
            place["y"],
            "matched",
        ]
    else:
        center = district_center_coordinates.get(str(row["sgg_cd"]).zfill(5))
        if center is not None:
            longitude, latitude = center
            result_df.loc[
                index,
                [
                    "kakao_place_id",
                    "kakao_place_nm",
                    "category_nm",
                    "address_nm",
                    "road_address_nm",
                    "longitude",
                    "latitude",
                    "search_status",
                ],
            ] = [
                "",
                f"{row['sgg_nm']} 중심점",
                "시군구 중심점",
                f"부산광역시 {row['sgg_nm']}",
                "",
                str(longitude),
                str(latitude),
                "district_center",
            ]
        else:
            result_df.at[index, "search_status"] = "not_found"

    if count % 100 == 0:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"{count:,}건 처리")

    time.sleep(0.1)

result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"저장 완료: {output_path}")
print(result_df["search_status"].value_counts(dropna=False))
