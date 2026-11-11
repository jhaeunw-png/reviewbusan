import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from dotenv import load_dotenv
from matplotlib.patches import Patch
from sqlalchemy import create_engine


load_dotenv("./database/.env")

port = os.getenv("DB_PORT")
user = os.getenv("MYSQL_USER")
database = os.getenv("MYSQL_DATABASE")
password = os.getenv("MYSQL_PASSWORD")
host = os.getenv("HOST", "localhost")

db_info = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_info)

visitor_df = pd.read_sql(
    """
    SELECT
        t.sgg_cd,
        d.sgg_nm,
        n.nationality_nm,
        SUM(t.visitor_counts) AS tourist_cnt
    FROM nationality_visitor_counts t
    JOIN sigungu d ON t.sgg_cd = d.sgg_cd
    JOIN nationalities n ON t.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY t.sgg_cd, d.sgg_nm, n.nationality_id, n.nationality_nm
    """,
    con=engine,
)
engine.dispose()

zone_info = {
    "원도심": {"codes": ["26110", "26140", "26170", "26200"], "color": "#F4A261"},
    "중부산": {"codes": ["26230", "26290", "26500", "26470"], "color": "#76C893"},
    "서부산": {"codes": ["26320", "26380", "26440", "26530"], "color": "#4EA8DE"},
    "동부산": {"codes": ["26410", "26260", "26350", "26710"], "color": "#9B8AFB"},
}

country_order = (
    visitor_df.groupby("nationality_nm")["tourist_cnt"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
district_order = [code for zone in zone_info.values() for code in zone["codes"]]
district_names = (
    visitor_df[["sgg_cd", "sgg_nm"]]
    .drop_duplicates()
    .set_index("sgg_cd")["sgg_nm"]
    .to_dict()
)
district_zones = {
    code: zone_name
    for zone_name, zone in zone_info.items()
    for code in zone["codes"]
}
district_colors = {
    code: zone["color"]
    for zone in zone_info.values()
    for code in zone["codes"]
}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization/구군_외국인_방문비율"
os.makedirs(output_path, exist_ok=True)

for country in country_order:
    fig, ax = plt.subplots(figsize=(10, 9))
    fig.patch.set_alpha(0)

    country_df = (
        visitor_df[visitor_df["nationality_nm"].eq(country)]
        .set_index("sgg_cd")
        .reindex(district_order, fill_value=0)
        .reset_index()
    )
    country_df["visit_rate"] = (
        country_df["tourist_cnt"] / country_df["tourist_cnt"].sum() * 100
    )
    labels = [
        f"{district_zones[code]}  {district_names[code]}"
        for code in district_order
    ]
    bars = ax.barh(
        labels,
        country_df["visit_rate"],
        color=[district_colors[code] for code in district_order],
        height=0.72,
    )
    ax.bar_label(
        bars,
        labels=[f"{value / 10_000:,.1f}만" for value in country_df["tourist_cnt"]],
        padding=4,
        fontsize=11,
    )
    for boundary in [3.5, 7.5, 11.5]:
        ax.axhline(boundary, color="#AEB8C2", linewidth=0.9)
    ax.set_xlim(0, country_df["visit_rate"].max() * 1.22)
    ax.invert_yaxis()
    ax.set_title(
        f"{country} 부산 구·군 방문 비율",
        fontsize=25,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel("해당 국가 방문객 중 비율", fontsize=13)
    ax.xaxis.set_major_formatter(ticker.PercentFormatter())
    ax.tick_params(axis="y", labelsize=12, length=0)
    ax.tick_params(axis="x", labelsize=11)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.set_facecolor("none")
    ax.spines[["top", "right", "left"]].set_visible(False)

    legend_handles = [
        Patch(facecolor=zone["color"], label=zone_name)
        for zone_name, zone in zone_info.items()
    ]
    ax.legend(
        handles=legend_handles,
        title="4권역",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=4,
        frameon=False,
        fontsize=11,
        title_fontsize=12,
    )
    fig.tight_layout()

    file_path = f"{output_path}/구군_외국인_방문비율_{country}.png"
    plt.savefig(file_path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close()
    print(f"저장 완료: {file_path}")
