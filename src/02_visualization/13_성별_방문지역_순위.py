import os

import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv(
    "data/results/방문자_성_연령.csv",
    dtype={"SGG_CD": "string"},
)

district_names = {
    "26110": "중구",
    "26140": "서구",
    "26170": "동구",
    "26200": "영도구",
    "26230": "부산진구",
    "26260": "동래구",
    "26290": "남구",
    "26320": "북구",
    "26350": "해운대구",
    "26380": "사하구",
    "26410": "금정구",
    "26440": "강서구",
    "26470": "연제구",
    "26500": "수영구",
    "26530": "사상구",
    "26710": "기장군",
}

df["district_nm"] = df["SGG_CD"].map(district_names)
df["tourist_cnt"] = pd.to_numeric(df["tourist_cnt"], errors="coerce")

gender_region_df = (
    df.groupby(["gender", "district_nm"], as_index=False)["tourist_cnt"]
    .sum()
)
gender_region_df["tourist_cnt"] = gender_region_df["tourist_cnt"] / 10_000

start_month = df["YEAR_MONTH"].min()
end_month = df["YEAR_MONTH"].max()

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)

gender_colors = {
    "남성": "#3F7CAC",
    "여성": "#E76F51",
}

chart_df = gender_region_df.pivot(
    index="district_nm",
    columns="gender",
    values="tourist_cnt",
).fillna(0)
chart_df["합계"] = chart_df["남성"] + chart_df["여성"]
chart_df = chart_df.sort_values("합계", ascending=True)
chart_df["남성_비율"] = chart_df["남성"] / chart_df["남성"].sum() * 100
chart_df["여성_비율"] = chart_df["여성"] / chart_df["여성"].sum() * 100

positions = range(len(chart_df))
bar_height = 0.36

fig, ax = plt.subplots(figsize=(11, 8.5))
male_bars = ax.barh(
    [position - bar_height / 2 for position in positions],
    chart_df["남성_비율"],
    height=bar_height,
    color=gender_colors["남성"],
    label="남성",
)
female_bars = ax.barh(
    [position + bar_height / 2 for position in positions],
    chart_df["여성_비율"],
    height=bar_height,
    color=gender_colors["여성"],
    label="여성",
)

ax.set_title("방문 지역 순위(남녀)", fontsize=27, fontweight="bold", pad=32)
ax.text(
    0.5,
    1.01,
    f"{start_month}~{end_month} 성별 누적 방문 비율",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=14,
    color="#666666",
)
ax.set_yticks(list(positions), chart_df.index)
ax.set_xlabel("방문 비율(%)", fontsize=14)
ax.set_ylabel("")
ax.tick_params(axis="x", labelsize=12)
ax.tick_params(axis="y", labelsize=13)
ax.grid(axis="x", color="#D9D9D9", linewidth=0.8, alpha=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.legend(loc="lower right", frameon=False, fontsize=12, ncol=2)

max_value = chart_df[["남성_비율", "여성_비율"]].max().max()
ax.set_xlim(0, max_value * 1.18)
for bars, counts in [(male_bars, chart_df["남성"]), (female_bars, chart_df["여성"])]:
    for bar, count in zip(bars, counts):
        ratio = bar.get_width()
        ax.text(
            ratio + max_value * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{count:,.0f}만 건",
            va="center",
            fontsize=9.5,
            color="#222222",
        )

fig.tight_layout()
plt.savefig(
    f"{output_path}/방문지역_순위_남녀.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

print(f"저장 완료: {output_path}/방문지역_순위_남녀.png")
