import os

import matplotlib.patheffects as path_effects
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

spending_df = pd.read_sql(
    """
    SELECT
        base_ym,
        n.nationality_nm,
        SUM(s.spend_amt) AS spend_amt
    FROM nationality_amounts s
    JOIN nationalities n
        ON s.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY s.base_ym, n.nationality_id, n.nationality_nm
    """,
    con=engine,
)

visitor_df = pd.read_sql(
    """
    SELECT
        t.base_ym,
        n.nationality_nm,
        SUM(t.visitor_counts) AS tourist_cnt
    FROM nationality_visitor_counts t
    JOIN nationalities n
        ON t.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY t.base_ym, n.nationality_id, n.nationality_nm
    """,
    con=engine,
)
engine.dispose()

monthly_df = spending_df.merge(
    visitor_df,
    on=["base_ym", "nationality_nm"],
    how="inner",
    validate="one_to_one",
)
monthly_df = monthly_df[monthly_df["tourist_cnt"] > 0].copy()
monthly_df["per_capita_spend"] = monthly_df["spend_amt"] / monthly_df["tourist_cnt"]
monthly_df = monthly_df[monthly_df["per_capita_spend"] > 0]

country_df = monthly_df.groupby("nationality_nm", as_index=False).agg(
    median_spend=("per_capita_spend", "median"),
    month_count=("base_ym", "count"),
)
country_df = country_df[country_df["month_count"] >= 12]
country_df = country_df.sort_values("median_spend")

countries = country_df["nationality_nm"].tolist()
country_groups = [
    countries[:len(countries) // 2],
    countries[len(countries) // 2:],
]

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

label_offset = country_df["median_spend"].max() * 0.015

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)

for group_number, group_countries in enumerate(country_groups, 1):
    group_df = country_df[country_df["nationality_nm"].isin(group_countries)]
    box_data = [
        monthly_df[monthly_df["nationality_nm"].eq(country)]["per_capita_spend"]
        for country in group_countries
    ]

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.boxplot(
        box_data,
        orientation="horizontal",
        tick_labels=group_countries,
        patch_artist=True,
        widths=0.6,
        showfliers=False,
        boxprops={"facecolor": "#9DC3E6", "edgecolor": "#2F75B5", "linewidth": 1.5},
        medianprops={"color": "#194B7A", "linewidth": 2.5},
        whiskerprops={"color": "#666666", "linewidth": 1.3},
        capprops={"color": "#666666", "linewidth": 1.3},
    )

    for position, (country, value) in enumerate(
        zip(group_df["nationality_nm"], group_df["median_spend"]),
        1,
    ):
        label_x = value + label_offset

        if country in ["대만", "프랑스", "튀르키예", "중국", "독일"]:
            values = box_data[position - 1]
            q1 = values.quantile(0.25)
            q3 = values.quantile(0.75)
            upper_whisker = values[values <= q3 + (q3 - q1) * 1.5].max()
            label_x = upper_whisker + label_offset

        ax.text(
            label_x,
            position,
            f"{value:,.0f}원",
            va="center",
            ha="left",
            fontsize=11,
            fontweight="bold",
            color="black",
            path_effects=[
                path_effects.Stroke(linewidth=3, foreground="white"),
                path_effects.Normal(),
            ],
        )

    ax.set_xlim(0, 2_000_000)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}원"))
    ax.set_title(
        f"국가별 외국인 1인당 관광소비 분포 ({group_number})",
        loc="center",
        fontsize=26,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel("월별 1인당 관광소비액(원)", fontsize=14)
    ax.grid(axis="x", which="major", color="#D9D9D9", linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=14)
    ax.tick_params(axis="x", labelsize=13)
    fig.tight_layout()

    file_path = f"{output_path}/국가별_1인당_소비분포_박스플롯_{group_number:02d}.png"
    plt.savefig(file_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"저장 완료: {file_path}")
