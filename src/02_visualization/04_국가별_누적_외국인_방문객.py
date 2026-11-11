import math
import os

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
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
target_year = os.getenv("TOURISM_TARGET_YEAR")
year_filter = "WHERE t.base_ym LIKE %(year_pattern)s" if target_year else ""

country_df = pd.read_sql(
    f"""
    SELECT
        n.nationality_nm AS region_nm,
        SUM(t.visitor_counts) AS tourist_cnt
    FROM nationality_visitor_counts t
    JOIN nationalities n
        ON t.nationality_id = n.nationality_id
    {year_filter}
    GROUP BY n.nationality_id, n.nationality_nm
    ORDER BY tourist_cnt DESC
    """,
    con=engine,
    params={"year_pattern": f"{target_year}-%"} if target_year else None,
)
engine.dispose()

country_df["tourist_cnt"] = pd.to_numeric(country_df["tourist_cnt"])
top_country_df = (
    country_df[country_df["region_nm"] != "기타"]
    .head(10)
    .copy()
    .reset_index(drop=True)
)
other_count = country_df[
    ~country_df["region_nm"].isin(top_country_df["region_nm"])
]["tourist_cnt"].sum()
top_country_df.loc[len(top_country_df)] = ["기타", other_count]

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

colors = [
    "#194B7A",
    "#2F75B5",
    "#5B9BD5",
    "#9DC3E6",
    "#70AD47",
    "#A5A5A5",
    "#FFC000",
    "#ED7D31",
    "#C55A11",
    "#8064A2",
    "#D9D9D9",
]

fig, ax = plt.subplots(figsize=(12, 7))
wedges, _, autotexts = ax.pie(
    top_country_df["tourist_cnt"],
    colors=colors,
    radius=0.82,
    startangle=90,
    counterclock=False,
    autopct="%1.1f%%",
    pctdistance=0.79,
    wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
)

total_count = top_country_df["tourist_cnt"].sum()

for index, text in enumerate(autotexts):
    percentage = top_country_df.iloc[index]["tourist_cnt"] / total_count * 100
    text.set_text(f"{percentage:.2f}%")
    text.set_fontsize(10)
    text.set_color("black")
    text.set_fontweight("bold")
    text.set_path_effects(
        [
            path_effects.Stroke(linewidth=3, foreground="white"),
            path_effects.Normal(),
        ]
    )

small_indexes = [
    index
    for index, value in enumerate(top_country_df["tourist_cnt"])
    if value / total_count * 100 < 2
]

for label_index, wedge_index in enumerate(small_indexes):
    angle = math.radians(
        (wedges[wedge_index].theta1 + wedges[wedge_index].theta2) / 2
    )
    label_y = 0.26 + label_index * 0.1
    autotexts[wedge_index].set_position((-0.88, label_y))
    autotexts[wedge_index].set_ha("right")
    ax.annotate(
        "",
        xy=(0.76 * math.cos(angle), 0.76 * math.sin(angle)),
        xytext=(-0.84, label_y),
        arrowprops={"arrowstyle": "-", "color": "#777777", "linewidth": 0.8},
    )

period_label = f"{target_year}년 외국인 방문객" if target_year else "누적 외국인 방문객"
chart_title = f"{target_year}년 국가별 외국인 방문객 비중" if target_year else "국가별 누적 외국인 방문객 비중"
output_name = f"{target_year}년_국가별_외국인_방문객_도넛.png" if target_year else "국가별_누적_외국인_방문객_도넛.png"

ax.text(0, 0.07, period_label, ha="center", va="center", fontsize=13, color="#666666")
ax.text(0, -0.07, f"{total_count:,.0f}명", ha="center", va="center", fontsize=20, fontweight="bold")

fig.text(
    0.68,
    0.78,
    "국가별 방문객 수",
    ha="center",
    fontsize=12,
    fontweight="bold",
)

for index, (_, row) in enumerate(top_country_df.iterrows()):
    y = 0.74 - index * 0.045
    fig.add_artist(
        plt.Rectangle(
            (0.59, y - 0.008),
            0.018,
            0.012,
            transform=fig.transFigure,
            color=colors[index],
            clip_on=False,
        )
    )
    fig.text(0.62, y, row["region_nm"], va="center", fontsize=10)
    fig.text(0.77, y, f"{row['tourist_cnt']:,.0f}명", ha="right", va="center", fontsize=10)

ax.text(
    0,
    0.90,
    chart_title,
    ha="center",
    va="bottom",
    fontsize=21,
    fontweight="bold",
)
fig.subplots_adjust(left=0.03, right=0.72, top=0.96, bottom=0.04)

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)
plt.savefig(
    f"{output_path}/{output_name}",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

print(f"저장 완료: {output_path}/{output_name}")
