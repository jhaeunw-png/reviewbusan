import os

import geopandas as gpd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from shapely.geometry import Point
from sqlalchemy import create_engine


load_dotenv("./database/.env")

port = os.getenv("DB_PORT")
user = os.getenv("MYSQL_USER")
database = os.getenv("MYSQL_DATABASE")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("HOST", "localhost")

db_info = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_info)

spending_df = pd.read_sql(
    """
    SELECT s.base_ym, n.nationality_nm, SUM(s.spend_amt) AS spend_amt
    FROM nationality_tourism_spending s
    JOIN nationalities n ON s.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY s.base_ym, n.nationality_id, n.nationality_nm
    """,
    con=engine,
)

visitor_df = pd.read_sql(
    """
    SELECT t.base_ym, n.nationality_nm, SUM(t.tourist_cnt) AS tourist_cnt
    FROM tourist_counts t
    JOIN nationalities n ON t.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY t.base_ym, n.nationality_id, n.nationality_nm
    """,
    con=engine,
)
engine.dispose()

country_codes = {
    "대만": "TWN", "독일": "DEU", "러시아": "RUS", "말레이시아": "MYS",
    "멕시코": "MEX", "몽골": "MNG", "미국": "USA", "베트남": "VNM",
    "사우디아라비아": "SAU", "싱가포르": "SGP", "아랍에미리트": "ARE", "영국": "GBR",
    "인도": "IND", "인도네시아": "IDN", "일본": "JPN", "중국": "CHN",
    "카자흐스탄": "KAZ", "캐나다": "CAN", "태국": "THA", "튀르키예": "TUR",
    "프랑스": "FRA", "필리핀": "PHL", "호주": "AUS", "홍콩": "HKG",
}

monthly_df = spending_df.merge(
    visitor_df,
    on=["base_ym", "nationality_nm"],
    how="inner",
    validate="one_to_one",
)
monthly_df = monthly_df[monthly_df["tourist_cnt"] > 0].copy()
monthly_df["per_capita_spend"] = monthly_df["spend_amt"] / monthly_df["tourist_cnt"]
country_df = (
    monthly_df[monthly_df["nationality_nm"].isin(country_codes)]
    .groupby("nationality_nm", as_index=False)
    .agg(
        median_spend=("per_capita_spend", "median"),
        month_count=("base_ym", "count"),
    )
)
country_df = country_df[country_df["month_count"] >= 12]
country_df["iso_a3"] = country_df["nationality_nm"].map(country_codes)

missing_countries = sorted(set(country_codes) - set(country_df["nationality_nm"]))
if missing_countries:
    raise ValueError(f"시각화할 데이터가 부족한 국가: {missing_countries}")

world = gpd.read_file(
    "https://naturalearth.s3.amazonaws.com/110m_cultural/ne_110m_admin_0_countries.zip"
)
world = world.merge(country_df, left_on="ADM0_A3", right_on="iso_a3", how="left")

label_points = world[world["nationality_nm"].notna()][
    ["nationality_nm", "geometry"]
].copy()
label_points["geometry"] = label_points.representative_point()
label_coordinates = {
    "영국": Point(-5.0, 58.0),
    "프랑스": Point(-1.0, 45.0),
    "독일": Point(13.0, 53.0),
    "튀르키예": Point(35.0, 39.0),
    "사우디아라비아": Point(39.0, 20.0),
    "아랍에미리트": Point(59.0, 27.0),
    "태국": Point(99.0, 17.0),
    "베트남": Point(110.0, 18.0),
    "말레이시아": Point(99.0, 5.0),
    "싱가포르": Point(103.8, -1.0),
    "인도네시아": Point(117.0, -7.0),
    "필리핀": Point(126.0, 13.0),
    "홍콩": Point(113.0, 25.0),
    "대만": Point(123.0, 27.0),
}
label_points = label_points[
    ~label_points["nationality_nm"].isin(label_coordinates)
]
label_points = gpd.GeoDataFrame(
    pd.concat(
        [
            label_points,
            pd.DataFrame(
                {
                    "nationality_nm": label_coordinates.keys(),
                    "geometry": label_coordinates.values(),
                }
            ),
        ],
        ignore_index=True,
    ),
    geometry="geometry",
    crs="EPSG:4326",
)

world = world.to_crs("EPSG:4326")
label_points = label_points.to_crs("EPSG:4326")

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(18, 10))
fig.patch.set_alpha(0)
ax.set_facecolor("none")
world.plot(ax=ax, color="#D9DEE3", edgecolor="#AEB6BF", linewidth=0.45)
world[world["nationality_nm"].notna()].plot(
    ax=ax,
    color="#8E7CF6",
    edgecolor="#6254B8",
    linewidth=0.9,
)

small_countries = label_points[
    label_points["nationality_nm"].isin(["싱가포르", "홍콩"])
]
ax.scatter(
    small_countries.geometry.x,
    small_countries.geometry.y,
    color="#8E7CF6",
    s=55,
    edgecolor="#333333",
    linewidth=0.7,
    zorder=5,
)

for _, row in label_points.iterrows():
    ax.annotate(
        row["nationality_nm"],
        xy=(row.geometry.x, row.geometry.y),
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="black",
        path_effects=[
            path_effects.Stroke(linewidth=3.5, foreground="white"),
            path_effects.Normal(),
        ],
    )

ax.set_xlim(-180, 180)
ax.set_ylim(-60, 90)
ax.axis("off")
fig.tight_layout()

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)
file_path = f"{output_path}/외국인_관광소비_대상국가_세계지도.png"
plt.savefig(file_path, dpi=200, bbox_inches="tight", transparent=True)
plt.close()

print(f"저장 완료: {file_path}")
