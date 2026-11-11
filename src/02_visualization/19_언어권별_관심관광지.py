import os

import matplotlib

matplotlib.use("Agg")

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
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

interest_df = pd.read_sql(
    """
    SELECT
        t.content_id,
        t.language,
        c.content_nm,
        SUM(t.visitor_counts) AS visitor_cnt
    FROM tourism_interest_counts t
    JOIN tourism_contents c
        ON t.content_id = c.content_id
    GROUP BY t.content_id, t.language, c.content_nm
    """,
    con=engine,
)
district_df = pd.read_sql(
    """
    SELECT sgg_cd, language, SUM(visitor_counts) AS visitor_cnt
    FROM tourism_interest_counts
    GROUP BY sgg_cd, language
    """,
    con=engine,
)
engine.dispose()

interest_df["visitor_cnt"] = pd.to_numeric(
    interest_df["visitor_cnt"], errors="coerce"
).fillna(0)

summary_df = (
    interest_df.groupby(
        ["content_id", "language", "content_nm"], as_index=False
    )["visitor_cnt"]
    .sum()
)

language_order = ["내국인", "영어권", "일본어", "중간체", "중번체"]
language_labels = {
    "내국인": "내국인",
    "영어권": "영어권",
    "일본어": "일어권",
    "중간체": "중국어(간체)",
    "중번체": "중국어(번체)",
}
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
language_colors = {
    "내국인": "#1F4E79",
    "영어권": "#2F75B5",
    "일본어": "#70AD47",
    "중간체": "#ED7D31",
    "중번체": "#8064A2",
}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization/언어권별_관심관광지"
os.makedirs(output_path, exist_ok=True)


def add_neon_effect(text, linewidth=3.5):
    text.set_path_effects(
        [
            path_effects.Stroke(linewidth=linewidth, foreground="white"),
            path_effects.Normal(),
        ]
    )


# 언어권별 관심 관광지 Top 10
for language in language_order:
    language_df = summary_df[summary_df["language"].eq(language)].copy()
    total_visitors = language_df["visitor_cnt"].sum()
    if total_visitors <= 0:
        continue

    language_df["visit_rate"] = language_df["visitor_cnt"] / total_visitors * 100
    chart_df = language_df.nlargest(10, "visitor_cnt").sort_values("visit_rate")

    fig, ax = plt.subplots(figsize=(12, 8.5))
    bars = ax.barh(
        chart_df["content_nm"],
        chart_df["visit_rate"],
        color=language_colors[language],
        height=0.68,
    )

    x_max = max(chart_df["visit_rate"].max(), 1)
    ax.set_xlim(0, x_max * 1.32)
    for bar, rate, count in zip(
        bars, chart_df["visit_rate"], chart_df["visitor_cnt"]
    ):
        label = ax.text(
            rate + x_max * 0.018,
            bar.get_y() + bar.get_height() / 2,
            f"{rate:.1f}% · {count / 10_000:,.1f}만 건",
            ha="left",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="black",
        )
        add_neon_effect(label)

    display_language = language_labels[language]
    ax.set_title(
        f"{display_language} 관심 관광지 Top 10",
        fontsize=27,
        fontweight="bold",
        pad=20,
    )
    ax.set_xlabel(f"{display_language} 전체 관심 관광지 방문 중 비율", fontsize=14)
    ax.xaxis.set_major_formatter(ticker.PercentFormatter())
    ax.tick_params(axis="x", labelsize=12)
    ax.tick_params(axis="y", labelsize=13, length=0)
    ax.grid(axis="x", color="#D9D9D9", linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout()

    file_path = f"{output_path}/관심관광지_방문순위_{display_language}.png"
    plt.savefig(file_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"저장 완료: {file_path}")


# 전체 누적 방문 상위 20개 관광지의 언어권별 내부 방문 비율 히트맵
top_content_ids = (
    summary_df.groupby("content_id")["visitor_cnt"]
    .sum()
    .nlargest(20)
    .index
)
heatmap_source = summary_df[summary_df["content_id"].isin(top_content_ids)].copy()
language_totals = summary_df.groupby("language")["visitor_cnt"].sum()
heatmap_source["visit_rate"] = (
    heatmap_source["visitor_cnt"]
    / heatmap_source["language"].map(language_totals)
    * 100
)

heatmap_df = heatmap_source.pivot_table(
    index="content_nm",
    columns="language",
    values="visit_rate",
    aggfunc="sum",
    fill_value=0,
).reindex(columns=language_order, fill_value=0)

row_order = (
    heatmap_source.groupby("content_nm")["visitor_cnt"]
    .sum()
    .sort_values(ascending=False)
    .index
)
heatmap_df = heatmap_df.reindex(row_order)

fig, ax = plt.subplots(figsize=(12, 11))
image = ax.imshow(heatmap_df.to_numpy(), cmap="Blues", aspect="auto")

ax.set_xticks(
    np.arange(len(language_order)),
    [language_labels[language] for language in language_order],
)
ax.set_yticks(np.arange(len(heatmap_df.index)), heatmap_df.index)
ax.tick_params(axis="x", labelsize=13, top=True, bottom=False, labeltop=True)
ax.tick_params(axis="y", labelsize=11, length=0)

threshold = heatmap_df.to_numpy().max() * 0.55
for row in range(heatmap_df.shape[0]):
    for column in range(heatmap_df.shape[1]):
        value = heatmap_df.iat[row, column]
        ax.text(
            column,
            row,
            f"{value:.1f}%",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white" if value >= threshold else "#222222",
        )

ax.set_title(
    "언어권별 관심 관광지 방문 비율 비교",
    fontsize=27,
    fontweight="bold",
    pad=24,
)
ax.spines[:].set_visible(False)
colorbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.025)
colorbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter())
colorbar.ax.tick_params(labelsize=10)
fig.tight_layout()

heatmap_path = f"{output_path}/언어권별_관심관광지_방문비율_히트맵.png"
plt.savefig(heatmap_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"저장 완료: {heatmap_path}")


# 각 언어권의 전체 관심 관광지 방문 건수 대비 구·군별 비율
district_df["sgg_cd"] = district_df["sgg_cd"].astype("string").str.zfill(5)
district_df["visitor_cnt"] = pd.to_numeric(
    district_df["visitor_cnt"], errors="coerce"
).fillna(0)
district_df = district_df[district_df["sgg_cd"].isin(district_names)].copy()
district_totals = district_df.groupby("language")["visitor_cnt"].sum()
district_df["visit_rate"] = (
    district_df["visitor_cnt"]
    / district_df["language"].map(district_totals).replace(0, np.nan)
    * 100
)
district_heatmap = district_df.pivot_table(
    index="sgg_cd",
    columns="language",
    values="visit_rate",
    aggfunc="sum",
    fill_value=0,
).reindex(index=district_order, columns=language_order, fill_value=0)

fig, ax = plt.subplots(figsize=(12, 9))
image = ax.imshow(district_heatmap.to_numpy(), cmap="Blues", aspect="auto")
ax.set_xticks(
    np.arange(len(language_order)),
    [language_labels[language] for language in language_order],
)
ax.set_yticks(
    np.arange(len(district_heatmap.index)),
    [
        f"{zone_name} · {district_names[code]}" if index == 0 else district_names[code]
        for zone_name, codes in district_zones.items()
        for index, code in enumerate(codes)
    ],
)
ax.tick_params(axis="x", labelsize=13, top=True, bottom=False, labeltop=True)
ax.tick_params(axis="y", labelsize=11, length=0)
for boundary in range(4, len(district_order), 4):
    ax.axhline(boundary - 0.5, color="white", linewidth=3)

threshold = district_heatmap.to_numpy().max() * 0.55
for row in range(district_heatmap.shape[0]):
    for column in range(district_heatmap.shape[1]):
        value = district_heatmap.iat[row, column]
        ax.text(
            column, row, f"{value:.1f}%",
            ha="center", va="center", fontsize=10, fontweight="bold",
            color="white" if value >= threshold else "#222222",
        )

ax.set_title("언어권별 구·군 관심 관광지 방문 비율", fontsize=25, fontweight="bold", pad=24)
ax.spines[:].set_visible(False)
colorbar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.025)
colorbar.ax.yaxis.set_major_formatter(ticker.PercentFormatter())
colorbar.ax.tick_params(labelsize=10)
fig.tight_layout()

district_heatmap_path = f"{output_path}/언어권별_구군_관심관광지_방문비율_히트맵.png"
plt.savefig(district_heatmap_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"저장 완료: {district_heatmap_path}")
