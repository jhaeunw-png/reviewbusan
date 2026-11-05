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

input_path = "data/results/관심_관광지_위치목록.csv"
output_path = "data/results/관심_관광지_위치목록_완료.csv"

district_names = {
    "26110": "중구", "26140": "서구", "26170": "동구", "26200": "영도구",
    "26230": "부산진구", "26260": "동래구", "26290": "남구", "26320": "북구",
    "26350": "해운대구", "26380": "사하구", "26410": "금정구", "26440": "강서구",
    "26470": "연제구", "26500": "수영구", "26530": "사상구", "26710": "기장군",
}

# 카카오 검색 실패 시 사용할 부산 구·군 중심점 좌표를 계산한다.
district_map = gpd.read_file("data/지적도/sig.shp")
district_map["SIG_CD"] = district_map["SIG_CD"].astype(str).str.zfill(5)
district_map = district_map[district_map["SIG_CD"].isin(district_names)].copy()

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

read_dtypes = {
    "content_id": "string",
    "sgg_cd": "string",
    "kakao_place_id": "string",
}

if os.path.exists(output_path):
    result_df = pd.read_csv(output_path, dtype=read_dtypes)
else:
    result_df = pd.read_csv(input_path, dtype=read_dtypes)

for column in location_columns:
    if column not in result_df.columns:
        result_df[column] = pd.Series(pd.NA, index=result_df.index, dtype="string")

# 문자열 값을 입력할 열을 미리 문자열형으로 통일해 LossySetitemError를 방지한다.
result_df[location_columns] = result_df[location_columns].astype("string")
result_df["sgg_cd"] = result_df["sgg_cd"].str.zfill(5)

headers = {"Authorization": f"KakaoAK {kakao_api_key}"}


def search_kakao_place(query):
    response = requests.get(
        "https://dapi.kakao.com/v2/local/search/keyword.json",
        headers=headers,
        params={"query": query, "size": 15},
        timeout=10,
    )
    response.raise_for_status()
    return response.json().get("documents", [])


def combined_address(place):
    return f"{place.get('address_name', '')} {place.get('road_address_name', '')}"


status = result_df["search_status"].fillna("").str.strip()
search_df = result_df[status.isin(["", "미수집", "not_found"])]

for count, (index, row) in enumerate(search_df.iterrows(), 1):
    sgg_nm = district_names.get(row["sgg_cd"], "")
    content_nm = str(row["content_nm"]).strip()
    query = f"부산광역시 {sgg_nm} {content_nm}".strip()
    fallback_query = f"부산광역시 {content_nm}"
    result_df.at[index, "search_query"] = query

    try:
        documents = search_kakao_place(query)
        has_busan_result = any(
            "부산" in combined_address(place) for place in documents
        )
        if not has_busan_result and fallback_query != query:
            documents = search_kakao_place(fallback_query)
    except requests.HTTPError as error:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        response = error.response
        status_code = response.status_code if response is not None else "unknown"
        response_text = response.text if response is not None else str(error)
        raise RuntimeError(
            f"Kakao API 오류 ({status_code}): {response_text}"
        ) from error
    except requests.RequestException:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        raise

    district_matches = [
        place
        for place in documents
        if sgg_nm and sgg_nm in combined_address(place)
    ]
    busan_matches = [
        place
        for place in documents
        if "부산" in combined_address(place)
    ]

    if district_matches:
        place = district_matches[0]
        search_status = "matched_sgg"
    elif busan_matches:
        place = busan_matches[0]
        search_status = "matched_busan"
    else:
        place = None
        search_status = "district_center"

    if place is not None:
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
            place.get("id", ""),
            place.get("place_name", ""),
            place.get("category_name", ""),
            place.get("address_name", ""),
            place.get("road_address_name", ""),
            place.get("x", ""),
            place.get("y", ""),
            search_status,
        ]
    else:
        center = district_center_coordinates.get(row["sgg_cd"])
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
                f"{sgg_nm} 중심점",
                "시군구 중심점",
                f"부산광역시 {sgg_nm}",
                "",
                str(longitude),
                str(latitude),
                search_status,
            ]
        else:
            result_df.at[index, "search_status"] = "not_found"

    if count % 50 == 0:
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"{count:,}건 처리")

    time.sleep(0.1)

result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"저장 완료: {output_path}")
print(result_df["search_status"].value_counts(dropna=False))
