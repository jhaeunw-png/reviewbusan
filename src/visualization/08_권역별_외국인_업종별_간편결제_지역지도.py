import os

import geopandas as gpd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
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

spending_df = pd.read_sql(
    """
    SELECT
        f.sgg_cd,
        d.sgg_nm,
        i.industry_nm,
        SUM(f.spend_amt) AS spend_amt
    FROM foreign_epay_spending f
    JOIN tourism_detail_industries di
        ON f.detail_industry_id = di.detail_industry_id
    JOIN tourism_industries i
        ON di.industry_id = i.industry_id
    JOIN districts d
        ON f.sgg_cd = d.sgg_cd
    GROUP BY f.sgg_cd, d.sgg_nm, i.industry_nm
    """,
    con=engine,
)
engine.dispose()

busan_map = gpd.read_file("data/지적도/sig.shp")
busan_map["SIG_CD"] = busan_map["SIG_CD"].astype(str)
busan_map = busan_map[busan_map["SIG_CD"].str.startswith("26")].copy()
busan_map = busan_map.merge(
    spending_df[["sgg_cd", "sgg_nm"]].drop_duplicates(),
    left_on="SIG_CD",
    right_on="sgg_cd",
    how="left",
)

industry_order = (
    spending_df.groupby("industry_nm")["spend_amt"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
color_map = {
    "식음료업": "#1F4E79",
    "쇼핑업": "#8E5EA2",
    "의료웰니스업": "#00A6A6",
    "여가서비스업": "#59A14F",
    "운송업": "#F2B701",
    "숙박업": "#E76F51",
    "여행업": "#7F7F7F",
}

district_industry_df = spending_df.pivot_table(
    index=["sgg_cd", "sgg_nm"],
    columns="industry_nm",
    values="spend_amt",
    aggfunc="sum",
    fill_value=0,
).reset_index().set_index("sgg_cd")

zone_info = {
    "원도심": {
        "codes": ["26110", "26140", "26170", "26200"],
        "color": "#F4A261",
        "offsets": {
            "26110": (-2600, 2200),
            "26140": (-3500, -800),
            "26170": (800, 700),
            "26200": (500, -1800),
        },
    },
    "중부산": {
        "codes": ["26230", "26290", "26500", "26470"],
        "color": "#76C893",
        "offsets": {
            "26230": (-3000, -1300),
            "26290": (1200, -1200),
            "26500": (1200, -2200),
            "26470": (800, 900),
        },
    },
    "동부산": {
        "codes": ["26410", "26260", "26350", "26710"],
        "color": "#9B8AFB",
        "offsets": {
            "26410": (-1600, 1000),
            "26260": (-1800, -1200),
            "26350": (-1000, -1000),
            "26710": (-1500, 500),
        },
    },
    "서부산": {
        "codes": ["26320", "26380", "26440", "26530"],
        "color": "#4EA8DE",
        "offsets": {
            "26320": (500, 1400),
            "26380": (1500, -1800),
            "26440": (-2500, -500),
            "26530": (1200, -500),
        },
    },
}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)

busan_zone_map = busan_map.copy()
for zone_name, zone in zone_info.items():
    busan_zone_map.loc[busan_zone_map["SIG_CD"].isin(zone["codes"]), "zone_nm"] = zone_name
    busan_zone_map.loc[busan_zone_map["SIG_CD"].isin(zone["codes"]), "zone_color"] = zone["color"]

min_x, min_y, max_x, max_y = busan_zone_map.total_bounds
min_y = max(min_y, 1664000)
map_width = max_x - min_x
map_height = max_y - min_y

fig, ax = plt.subplots(figsize=(12, 11))
for zone_name, zone in zone_info.items():
    zone_map = busan_zone_map[busan_zone_map["zone_nm"].eq(zone_name)]
    zone_map.plot(
        ax=ax,
        color=zone["color"],
        edgecolor="white",
        linewidth=1.0,
        zorder=1,
    )
    zone_point = zone_map.geometry.union_all().representative_point()
    zone_label = ax.text(
        zone_point.x,
        zone_point.y,
        zone_name,
        ha="center",
        va="center",
        fontsize=20,
        fontweight="bold",
        color="#222222",
        zorder=3,
    )
    zone_label.set_path_effects(
        [path_effects.Stroke(linewidth=4, foreground="white"), path_effects.Normal()]
    )

industry_handles = [
    Patch(facecolor=color_map[industry], edgecolor="none", label=industry)
    for industry in industry_order
]
ax.legend(
    handles=industry_handles,
    title="업종  |  단위: 천원",
    loc="lower center",
    bbox_to_anchor=(0.5, -0.04),
    ncol=4,
    frameon=False,
    fontsize=11,
    title_fontsize=12,
    columnspacing=1.4,
    handlelength=1.8,
)

ax.set_title(
    "부산 외국인 업종별 관광소비(간편결제)",
    fontsize=30,
    fontweight="bold",
    pad=24,
)
ax.set_xlim(min_x - map_width * 0.08, max_x + map_width * 0.10)
ax.set_ylim(min_y - map_height * 0.04, max_y + map_height * 0.08)
ax.set_axis_off()
fig.tight_layout()

plt.savefig(
    f"{output_path}/부산_외국인_업종별_관광소비_간편결제.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

print(f"저장 완료: {output_path}/부산_외국인_업종별_관광소비_간편결제.png")

for zone_name, zone in zone_info.items():
    zone_map = busan_map[busan_map["SIG_CD"].isin(zone["codes"])].copy()
    zone_values = district_industry_df.loc[zone["codes"], industry_order]
    max_value = zone_values.to_numpy().max()

    min_x, min_y, max_x, max_y = zone_map.total_bounds
    if zone_name == "서부산":
        min_y = max(min_y, 1666000)
    map_width = max_x - min_x
    map_height = max_y - min_y
    padding_x = map_width * 0.24
    padding_y = map_height * 0.22
    bar_max_width = map_width * 0.22
    bar_min_width = map_width * 0.015
    bar_height = map_height * 0.018
    bar_gap = map_height * 0.027

    fig, ax = plt.subplots(figsize=(10, 8))
    zone_map.plot(
        ax=ax,
        color=zone["color"],
        edgecolor="#AEB8C2",
        linewidth=1.2,
        zorder=1,
    )

    for _, district in zone_map.iterrows():
        sgg_cd = district["SIG_CD"]
        point = district.geometry.representative_point()
        dx, dy = zone["offsets"][sgg_cd]
        x = point.x + dx
        y = point.y + dy
        district_values = district_industry_df.loc[sgg_cd]

        ax.plot(
            [point.x, x],
            [point.y, y],
            color="#8C98A4",
            linewidth=1.0,
            zorder=3,
        )

        district_label = ax.text(
            x,
            y + bar_gap * 1.15,
            district_values["sgg_nm"],
            ha="left",
            va="bottom",
            fontsize=14,
            fontweight="bold",
            color="#222222",
            zorder=5,
        )
        district_label.set_path_effects(
            [path_effects.Stroke(linewidth=3, foreground="white"), path_effects.Normal()]
        )

        for index, industry in enumerate(industry_order):
            value = district_values[industry]
            if value <= 0:
                continue
            width = max(value / max_value * bar_max_width, bar_min_width)
            bar_y = y - index * bar_gap
            ax.barh(
                bar_y,
                width,
                height=bar_height,
                left=x,
                color=color_map[industry],
                edgecolor="white",
                linewidth=0.35,
                zorder=4,
            )
            value_label = ax.text(
                x + width + map_width * 0.008,
                bar_y,
                f"{value:,.0f}",
                ha="left",
                va="center",
                fontsize=10,
                color="#222222",
                zorder=5,
            )
            value_label.set_path_effects(
                [path_effects.Stroke(linewidth=2.5, foreground="white"), path_effects.Normal()]
            )

    ax.set_xlim(min_x - padding_x, max_x + padding_x)
    ax.set_ylim(min_y - padding_y, max_y + padding_y)
    ax.set_axis_off()
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.tight_layout()

    plt.savefig(
        f"{output_path}/{zone_name}_외국인_업종별_간편결제_지역지도.png",
        dpi=200,
        bbox_inches="tight",
        transparent=True,
    )
    plt.close()

    print(f"저장 완료: {output_path}/{zone_name}_외국인_업종별_간편결제_지역지도.png")
