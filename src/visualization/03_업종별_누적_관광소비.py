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

industry_df = pd.read_sql(
    """
    SELECT
        i.industry_nm,
        SUM(s.spend_amt) AS spend_amt
    FROM industry_tourism_spending s
    JOIN tourism_industries i
        ON s.industry_id = i.industry_id
    WHERE i.industry_nm <> '전체'
    GROUP BY i.industry_id, i.industry_nm
    ORDER BY spend_amt DESC
    """,
    con=engine,
)
engine.dispose()

industry_df["spend_amt"] = pd.to_numeric(industry_df["spend_amt"]) / 100_000_000

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

color_map = {
    "식음료업": "#1F4E79",
    "쇼핑업": "#8E5EA2",
    "의료웰니스업": "#00A6A6",
    "여가서비스업": "#59A14F",
    "운송업": "#F2B701",
    "숙박업": "#E76F51",
    "여행업": "#7F7F7F",
}
colors = [color_map[industry] for industry in industry_df["industry_nm"]]

fig, ax = plt.subplots(figsize=(12, 7))
wedges, _, autotexts = ax.pie(
    industry_df["spend_amt"],
    colors=colors,
    radius=0.82,
    startangle=90,
    counterclock=False,
    autopct="%1.1f%%",
    pctdistance=0.79,
    wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
)

total_amount = industry_df["spend_amt"].sum()

for index, text in enumerate(autotexts):
    percentage = industry_df.iloc[index]["spend_amt"] / total_amount * 100
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
    for index, value in enumerate(industry_df["spend_amt"])
    if value / total_amount * 100 < 2
]

for label_index, wedge_index in enumerate(small_indexes):
    angle = math.radians(
        (wedges[wedge_index].theta1 + wedges[wedge_index].theta2) / 2
    )
    label_y = 0.56 + label_index * 0.1
    autotexts[wedge_index].set_position((-0.88, label_y))
    autotexts[wedge_index].set_ha("right")
    ax.annotate(
        "",
        xy=(0.76 * math.cos(angle), 0.76 * math.sin(angle)),
        xytext=(-0.84, label_y),
        arrowprops={"arrowstyle": "-", "color": "#777777", "linewidth": 0.8},
    )

ax.text(0, 0.07, "누적 관광소비", ha="center", va="center", fontsize=13, color="#666666")
ax.text(0, -0.07, f"{total_amount:,.2f}억원", ha="center", va="center", fontsize=20, fontweight="bold")

fig.text(
    0.665,
    0.69,
    "업종별 소비금액",
    ha="center",
    fontsize=12,
    fontweight="bold",
)

for index, (_, row) in enumerate(industry_df.iterrows()):
    y = 0.65 - index * 0.055
    amount_label = f"{row['spend_amt']:,.2f}억원"
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
    fig.text(0.62, y, row["industry_nm"], va="center", fontsize=10)
    fig.text(0.74, y, amount_label, ha="right", va="center", fontsize=10)

ax.text(
    0,
    0.90,
    "업종별 누적 관광소비 비중",
    ha="center",
    va="bottom",
    fontsize=21,
    fontweight="bold",
)
fig.subplots_adjust(left=0.03, right=0.72, top=0.96, bottom=0.04)

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)
plt.savefig(
    f"{output_path}/업종별_누적_관광소비_도넛.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

print(f"저장 완료: {output_path}/업종별_누적_관광소비_도넛.png")
