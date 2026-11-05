import os
import re

import matplotlib

matplotlib.use("Agg")

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

spending_df = pd.read_sql(
    """
    SELECT
        s.sgg_cd,
        d.sgg_nm,
        n.nationality_nm,
        i.industry_nm,
        SUM(s.spend_amt) AS spend_amt
    FROM foreign_epay_spending s
    JOIN districts d
        ON s.sgg_cd = d.sgg_cd
    JOIN nationalities n
        ON s.nationality_id = n.nationality_id
    JOIN tourism_detail_industries di
        ON s.detail_industry_id = di.detail_industry_id
    JOIN tourism_industries i
        ON di.industry_id = i.industry_id
    WHERE n.nationality_nm <> '기타'
    GROUP BY
        s.sgg_cd,
        d.sgg_nm,
        n.nationality_id,
        n.nationality_nm,
        i.industry_id,
        i.industry_nm
    """,
    con=engine,
)
engine.dispose()

spending_df["sgg_cd"] = spending_df["sgg_cd"].astype(str).str.zfill(5)
spending_df["spend_amt"] = pd.to_numeric(
    spending_df["spend_amt"], errors="coerce"
).fillna(0)
# 원본 단위가 천 원이므로 100,000으로 나누면 억 원 단위가 된다.
spending_df["spend_eok"] = spending_df["spend_amt"] / 100_000

district_order = (
    spending_df[["sgg_cd", "sgg_nm"]]
    .drop_duplicates()
    .sort_values("sgg_cd")
)
country_order = (
    spending_df.groupby("nationality_nm")["spend_amt"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)
industry_order = (
    spending_df.groupby("industry_nm")["spend_amt"]
    .sum()
    .sort_values(ascending=False)
    .index.tolist()
)

industry_palette = [
    "#1F4E79", "#2F75B5", "#5B9BD5", "#70AD47",
    "#ED7D31", "#FFC000", "#A5A5A5", "#8064A2",
]
industry_colors = {
    industry: industry_palette[index % len(industry_palette)]
    for index, industry in enumerate(industry_order)
}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

output_root = "data/results/visualization/국가별_구군별_소비유형"
os.makedirs(output_root, exist_ok=True)


def safe_filename(value):
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(value))
    return value.strip().rstrip(".")


saved_count = 0

for country in country_order:
    safe_country = safe_filename(country)
    country_path = f"{output_root}/{safe_country}"
    os.makedirs(country_path, exist_ok=True)

    for _, district in district_order.iterrows():
        sgg_cd = district["sgg_cd"]
        sgg_nm = district["sgg_nm"]
        safe_district_nm = safe_filename(sgg_nm)
        chart_df = spending_df[
            spending_df["sgg_cd"].eq(sgg_cd)
            & spending_df["nationality_nm"].eq(country)
        ].copy()
        if chart_df.empty or chart_df["spend_eok"].sum() <= 0:
            continue

        chart_df = (
            chart_df.set_index("industry_nm")["spend_eok"]
            .reindex(industry_order, fill_value=0)
            .rename_axis("industry_nm")
            .reset_index()
        )

        chart_df = chart_df[chart_df["spend_eok"] > 0].copy()
        pie_labels = chart_df["industry_nm"].tolist()
        label_index = iter(pie_labels)

        def format_inner_label(pct):
            industry = next(label_index)
            if pct < 3:
                return ""
            return f"{industry}\n{pct:.1f}%"

        fig, ax = plt.subplots(figsize=(14, 10))
        fig.patch.set_alpha(0)
        ax.set_facecolor("none")
        wedges, label_texts, percent_texts = ax.pie(
            chart_df["spend_eok"],
            labels=None,
            colors=[industry_colors[name] for name in chart_df["industry_nm"]],
            autopct=format_inner_label,
            startangle=90,
            counterclock=False,
            pctdistance=0.7,
            wedgeprops={"width": 0.58, "edgecolor": "white", "linewidth": 1.5},
            textprops={"fontsize": 13, "fontweight": "bold", "color": "black"},
        )

        center_text = ax.text(
            0,
            0,
            sgg_nm,
            ha="center",
            va="center",
            fontsize=25,
            fontweight="bold",
            color="black",
        )
        center_text.set_path_effects(
            [
                path_effects.Stroke(linewidth=4.5, foreground="white"),
                path_effects.Normal(),
            ]
        )

        rates = chart_df["spend_eok"] / chart_df["spend_eok"].sum() * 100
        for text, rate in zip(percent_texts, rates):
            text.set_fontsize(11 if rate < 5 else 13)
            text.set_fontweight("bold")
            text.set_color("black")
            text.set_path_effects(
                [
                    path_effects.Stroke(linewidth=4, foreground="white"),
                    path_effects.Normal(),
                ]
            )

        ax.legend(
            wedges,
            chart_df["industry_nm"],
            title="소비유형",
            loc="upper center",
            bbox_to_anchor=(0.5, -0.04),
            ncol=4,
            frameon=False,
            fontsize=13,
            title_fontsize=14,
        )
        ax.axis("equal")
        fig.tight_layout(rect=[0, 0.08, 1, 1])

        file_path = (
            f"{country_path}/소비유형_{safe_district_nm}_{safe_country}.png"
        )
        plt.savefig(
            file_path,
            dpi=200,
            bbox_inches="tight",
            transparent=True,
        )
        plt.close()
        saved_count += 1

    print(f"저장 완료: {country_path}")

print(f"총 {saved_count:,}개 이미지 저장 완료: {output_root}")
