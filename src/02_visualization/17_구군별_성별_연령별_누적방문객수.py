import os

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd


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
gender_order = ["남성", "여성"]
gender_colors = {"남성": "#3F7CAC", "여성": "#E76F51"}

df["district_nm"] = df["SGG_CD"].map(district_names)
df["tourist_cnt"] = pd.to_numeric(df["tourist_cnt"], errors="coerce")
df = df.dropna(subset=["district_nm", "AGEG_DIV_NM", "gender", "tourist_cnt"])

summary_df = (
    df.groupby(
        ["SGG_CD", "district_nm", "AGEG_DIV_NM", "gender"],
        as_index=False,
    )["tourist_cnt"]
    .sum()
)

start_month = df["YEAR_MONTH"].min()
end_month = df["YEAR_MONTH"].max()

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_path = "data/results/visualization/구군별_성별_연령별_누적방문객수"
os.makedirs(output_path, exist_ok=True)

x = np.arange(len(age_order))
bar_width = 0.36

for sgg_cd, district_nm in district_names.items():
    district_df = summary_df[summary_df["SGG_CD"].eq(sgg_cd)]
    chart_df = (
        district_df.pivot_table(
            index="AGEG_DIV_NM",
            columns="gender",
            values="tourist_cnt",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(index=age_order, columns=gender_order, fill_value=0)
    )
    chart_df = chart_df / 10_000

    fig, ax = plt.subplots(figsize=(13, 8))
    male_bars = ax.bar(
        x - bar_width / 2,
        chart_df["남성"],
        width=bar_width,
        color=gender_colors["남성"],
        label="남성",
    )
    female_bars = ax.bar(
        x + bar_width / 2,
        chart_df["여성"],
        width=bar_width,
        color=gender_colors["여성"],
        label="여성",
    )

    y_max = max(chart_df.to_numpy().max(), 1)
    ax.set_ylim(0, y_max * 1.18)

    for bars in [male_bars, female_bars]:
        for bar in bars:
            value = bar.get_height()
            if value <= 0:
                continue
            label = ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + y_max * 0.015,
                f"{value:,.0f}만\n건",
                ha="center",
                va="bottom",
                fontsize=9.5,
                linespacing=0.9,
                fontweight="bold",
                color="black",
            )
            label.set_path_effects(
                [
                    path_effects.Stroke(linewidth=3, foreground="white"),
                    path_effects.Normal(),
                ]
            )

    ax.set_title(
        f"{district_nm} 성별·연령별 누적 방문객 수",
        fontsize=27,
        fontweight="bold",
        pad=32,
    )
    ax.text(
        0.5,
        1.01,
        f"{start_month}~{end_month}",
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=15,
        color="#666666",
    )
    ax.set_xticks(x, age_order)
    ax.set_xlabel("연령대", fontsize=14)
    ax.set_ylabel("누적 방문객 수(만 건)", fontsize=14)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}만"))
    ax.tick_params(axis="x", labelsize=13)
    ax.tick_params(axis="y", labelsize=12)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        loc="upper right",
        frameon=False,
        fontsize=13,
        ncol=2,
    )
    fig.tight_layout()

    file_path = f"{output_path}/성별_연령별_누적방문객수_{district_nm}.png"
    plt.savefig(file_path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"저장 완료: {file_path}")
