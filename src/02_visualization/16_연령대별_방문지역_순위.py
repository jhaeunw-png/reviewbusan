import os

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from matplotlib.patches import Patch


df = pd.read_csv(
    "data/results/방문자_성_연령.csv",
    dtype={"SGG_CD": "string"},
)

district_names = {
    "26110": "중구", "26140": "서구", "26170": "동구", "26200": "영도구",
    "26230": "부산진구", "26260": "동래구", "26290": "남구", "26320": "북구",
    "26350": "해운대구", "26380": "사하구", "26410": "금정구", "26440": "강서구",
    "26470": "연제구", "26500": "수영구", "26530": "사상구", "26710": "기장군",
}
age_order = [
    "0~9세", "10~19세", "20~29세", "30~39세",
    "40~49세", "50~59세", "60~69세", "70세 이상",
]
district_colors = [
    "#D95F0E", "#F16913", "#FD8D3C", "#FDAE6B",
    "#238B45", "#41AB5D", "#74C476", "#A1D99B",
    "#2171B5", "#4292C6", "#6BAED6", "#9ECAE1",
    "#6A51A3", "#807DBA", "#9E9AC8", "#BCBDDC",
]

df["district_nm"] = df["SGG_CD"].map(district_names)
df["tourist_cnt"] = pd.to_numeric(df["tourist_cnt"], errors="coerce")

age_region_df = (
    df.groupby(["AGEG_DIV_NM", "district_nm"], as_index=False)["tourist_cnt"]
    .sum()
)
chart_df = age_region_df.pivot(
    index="AGEG_DIV_NM",
    columns="district_nm",
    values="tourist_cnt",
).fillna(0)
district_order = (
    chart_df.sum(axis=0)
    .sort_values(ascending=False)
    .index.tolist()
)
chart_df = chart_df.reindex(age_order)[district_order]
rate_df = chart_df.div(chart_df.sum(axis=1), axis=0) * 100

start_month = df["YEAR_MONTH"].min()
end_month = df["YEAR_MONTH"].max()

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)

fig, ax = plt.subplots(figsize=(18, 10))
left = pd.Series(0.0, index=age_order)

for district, color in zip(district_order, district_colors):
    rates = rate_df[district]
    counts = chart_df[district]
    bars = ax.barh(
        age_order,
        rates,
        left=left,
        color=color,
        edgecolor="white",
        linewidth=0.8,
        height=0.72,
    )
    for bar, rate, count in zip(bars, rates, counts):
        if rate < 3:
            continue
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_y() + bar.get_height() / 2,
            f"{district}\n{rate:.1f}%\n{count / 10_000:,.0f}만 건",
            ha="center",
            va="center",
            fontsize=9,
            linespacing=0.95,
            color="black",
            fontweight="bold",
            path_effects=[
                path_effects.Stroke(linewidth=3, foreground="white"),
                path_effects.Normal(),
            ],
        )
    left += rates

ax.set_title("연령대별 방문 지역 구성", fontsize=29, fontweight="bold", pad=34)
ax.text(
    0.5,
    1.01,
    f"{start_month}~{end_month} · 막대별 전체 100%",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=15,
    color="#666666",
)
ax.set_xlim(0, 100)
ax.invert_yaxis()
ax.set_xlabel("연령대별 지역 방문 비율", fontsize=15)
ax.xaxis.set_major_formatter(ticker.PercentFormatter())
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=15, length=0)
ax.grid(axis="x", color="#D9D9D9", linewidth=0.8, alpha=0.7)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)

legend_handles = [
    Patch(facecolor=color, label=district)
    for district, color in zip(district_order, district_colors)
]
ax.legend(
    handles=legend_handles,
    title="구·군",
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12),
    ncol=8,
    frameon=False,
    fontsize=10,
    title_fontsize=11,
)
fig.tight_layout()

file_path = f"{output_path}/연령대별_방문지역_구성.png"
plt.savefig(file_path, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"저장 완료: {file_path}")
