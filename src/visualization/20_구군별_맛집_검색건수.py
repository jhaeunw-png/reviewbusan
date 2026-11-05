import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv("./database/.env")

port = os.getenv("DB_PORT")
user = os.getenv("MYSQL_USER")
database = os.getenv("MYSQL_DATABASE")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("HOST", "localhost")

db_info = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_info)
try:
    search_df = pd.read_sql(
        """
        SELECT n.sgg_cd, n.audience_type, SUM(n.search_cnt) AS search_cnt
        FROM navigation_search_counts n
        JOIN tourism_places p ON n.poi_id = p.poi_id
        WHERE p.place_type = '맛집'
          AND n.audience_type IN ('외지인', '현지인')
        GROUP BY n.sgg_cd, n.audience_type
        """,
        con=engine,
    )
finally:
    engine.dispose()

district_names = {
    "26110": "중구", "26140": "서구", "26170": "동구", "26200": "영도구",
    "26230": "부산진구", "26260": "동래구", "26290": "남구", "26320": "북구",
    "26350": "해운대구", "26380": "사하구", "26410": "금정구", "26440": "강서구",
    "26470": "연제구", "26500": "수영구", "26530": "사상구", "26710": "기장군",
}
district_zones = {
    "원도심": ["26110", "26140", "26170", "26200"],
    "중부산": ["26230", "26290", "26500", "26470"],
    "서부산": ["26320", "26380", "26440", "26530"],
    "동부산": ["26410", "26260", "26350", "26710"],
}
district_order = [code for codes in district_zones.values() for code in codes]
audience_order = ["외지인", "현지인"]

search_df["sgg_cd"] = search_df["sgg_cd"].astype("string").str.zfill(5)
search_df["search_cnt"] = pd.to_numeric(
    search_df["search_cnt"], errors="coerce"
).fillna(0)
chart_df = search_df.pivot_table(
    index="sgg_cd",
    columns="audience_type",
    values="search_cnt",
    aggfunc="sum",
    fill_value=0,
).reindex(index=district_order, columns=audience_order, fill_value=0)

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(12, 9))
positions = range(len(district_order))
left = pd.Series(0, index=chart_df.index, dtype="float64")
for audience, color in [("외지인", "#2F75B5"), ("현지인", "#70AD47")]:
    values = chart_df[audience]
    ax.barh(positions, values, left=left, height=0.68, label=audience, color=color)
    left += values

labels = [
    f"{zone} · {district_names[code]}" if index == 0 else district_names[code]
    for zone, codes in district_zones.items()
    for index, code in enumerate(codes)
]
ax.set_yticks(list(positions), labels)
ax.invert_yaxis()
for boundary in range(4, len(district_order), 4):
    ax.axhline(boundary - 0.5, color="#D9D9D9", linewidth=1)

ax.set_title("구·군별 맛집 내비게이션 검색 건수", fontsize=24, fontweight="bold", pad=18)
ax.set_xlabel("누적 검색 건수", fontsize=13)
ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}"))
ax.tick_params(axis="x", labelsize=11)
ax.tick_params(axis="y", labelsize=11, length=0)
ax.grid(axis="x", color="#D9D9D9", alpha=0.7)
ax.set_axisbelow(True)
ax.legend(title="검색자 구분", loc="lower right")
ax.spines[["top", "right", "left"]].set_visible(False)
fig.tight_layout()

output_path = "data/results/visualization/구군별_맛집_검색건수.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"저장 완료: {output_path}")
