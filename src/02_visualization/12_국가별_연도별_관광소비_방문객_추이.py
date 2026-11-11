import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
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
        s.base_ym,
        n.nationality_nm,
        SUM(s.spend_amt) AS spend_amt
    FROM nationality_amounts s
    JOIN nationalities n
        ON s.nationality_id = n.nationality_id
    WHERE n.nationality_nm <> '기타' AND s.base_ym >= '2023-01'
    GROUP BY s.base_ym, n.nationality_id, n.nationality_nm
    ORDER BY s.base_ym, n.nationality_nm
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
    WHERE n.nationality_nm <> '기타' AND t.base_ym >= '2023-01'
    GROUP BY t.base_ym, n.nationality_id, n.nationality_nm
    ORDER BY t.base_ym, n.nationality_nm
    """,
    con=engine,
)
engine.dispose()

spending_df["date"] = pd.to_datetime(spending_df["base_ym"])
visitor_df["date"] = pd.to_datetime(visitor_df["base_ym"])

per_capita_df = spending_df[["base_ym", "date", "nationality_nm", "spend_amt"]].merge(
    visitor_df[["base_ym", "nationality_nm", "tourist_cnt"]],
    on=["base_ym", "nationality_nm"],
    how="inner",
    validate="one_to_one",
)
per_capita_df = per_capita_df[per_capita_df["tourist_cnt"] > 0].copy()
per_capita_df["per_capita_spend"] = (
    per_capita_df["spend_amt"] / per_capita_df["tourist_cnt"]
)

spending_2025 = (
    spending_df[spending_df["date"].dt.year.eq(2025)]
    .groupby("nationality_nm", as_index=False)["spend_amt"].sum()
)
visitor_2025 = (
    visitor_df[visitor_df["date"].dt.year.eq(2025)]
    .groupby("nationality_nm", as_index=False)["tourist_cnt"].sum()
)
per_capita_2025 = spending_2025.merge(visitor_2025, on="nationality_nm")
per_capita_2025["per_capita_spend"] = (
    per_capita_2025["spend_amt"] / per_capita_2025["tourist_cnt"]
)

top_spending_countries = spending_2025.nlargest(10, "spend_amt")["nationality_nm"].tolist()
top_visitor_countries = visitor_2025.nlargest(10, "tourist_cnt")["nationality_nm"].tolist()
top_per_capita_countries = per_capita_2025.nlargest(
    5, "per_capita_spend"
)["nationality_nm"].tolist()
all_per_capita_countries = per_capita_2025.sort_values(
    "per_capita_spend", ascending=False
)["nationality_nm"].tolist()
seasonality_df = per_capita_df[
    per_capita_df["nationality_nm"].isin(all_per_capita_countries)
].copy()

spending_df = spending_df[spending_df["nationality_nm"].isin(top_spending_countries)].copy()
visitor_df = visitor_df[visitor_df["nationality_nm"].isin(top_visitor_countries)].copy()
per_capita_df = per_capita_df[
    per_capita_df["nationality_nm"].isin(top_per_capita_countries)
].copy()
spending_df["spend_amt"] = spending_df["spend_amt"] / 100_000_000
visitor_df["tourist_cnt"] = visitor_df["tourist_cnt"] / 10_000
all_months = pd.date_range(
    min(spending_df["date"].min(), visitor_df["date"].min()),
    max(spending_df["date"].max(), visitor_df["date"].max()),
    freq="MS",
)

colors = [
    "#1F4E79",
    "#8E5EA2",
    "#00A6A6",
    "#59A14F",
    "#F2B701",
    "#E76F51",
    "#7F7F7F",
    "#4EA8DE",
    "#C55A11",
    "#8064A2",
]

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(18, 7))
for index, country in enumerate(top_spending_countries):
    country_df = spending_df[spending_df["nationality_nm"].eq(country)]
    ax.plot(
        country_df["date"],
        country_df["spend_amt"],
        marker="o",
        markersize=4,
        linewidth=1.8,
        color=colors[index],
        label=country,
    )

ax.set_title("국가별 월별 관광소비 추이", fontsize=26, fontweight="bold", pad=34)
ax.text(
    0.5,
    1.01,
    "관광소비액",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=15,
    color="#666666",
)
ax.set_xlabel("년월", fontsize=14)
ax.set_ylabel("관광소비액(억원)", fontsize=14)
ax.set_xticks(all_months)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.tick_params(axis="both", labelsize=12)
ax.tick_params(axis="x", labelrotation=90, labelsize=8)
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(
    title="국가",
    loc="upper left",
    bbox_to_anchor=(1.01, 1),
    frameon=False,
    fontsize=11,
    title_fontsize=12,
)
fig.tight_layout()

output_path = "data/results/visualization"
os.makedirs(output_path, exist_ok=True)
plt.savefig(
    f"{output_path}/국가별_월별_관광소비액_추이.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

fig, ax = plt.subplots(figsize=(18, 7.5))
for index, country in enumerate(top_per_capita_countries):
    country_df = per_capita_df[per_capita_df["nationality_nm"].eq(country)]
    ax.plot(
        country_df["date"],
        country_df["per_capita_spend"],
        marker="o",
        markersize=4,
        linewidth=1.8,
        color=colors[index],
        label=country,
    )

ax.set_title("국가별 월별 1인당 관광소비 추이", fontsize=26, fontweight="bold", pad=34)
ax.text(
    0.5,
    1.01,
    "1인당 관광소비액",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=15,
    color="#666666",
)
ax.set_xlabel("년월", fontsize=14)
ax.set_ylabel("1인당 관광소비액(원)", fontsize=14)
ax.set_xticks(all_months)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}원"))
ax.tick_params(axis="both", labelsize=12)
ax.tick_params(axis="x", labelrotation=90, labelsize=8)
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.75)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(
    title="국가",
    loc="upper left",
    bbox_to_anchor=(1.01, 1),
    frameon=False,
    fontsize=11,
    title_fontsize=12,
)
fig.tight_layout()

plt.savefig(
    f"{output_path}/국가별_월별_1인당_관광소비액_추이.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

seasonal_countries = ["싱가포르", "인도네시아", "일본", "말레이시아", "중국"]
year_colors = {
    2023: "#1F4E79",
    2024: "#59A14F",
    2025: "#E76F51",
    2026: "#8E5EA2",
}

for country in seasonal_countries:
    country_df = seasonality_df[
        seasonality_df["nationality_nm"].eq(country)
    ].copy()
    country_df["year"] = country_df["date"].dt.year
    country_df["month"] = country_df["date"].dt.month

    fig, ax = plt.subplots(figsize=(12, 7))
    for year in sorted(country_df["year"].unique()):
        year_df = country_df[country_df["year"].eq(year)].sort_values("month")
        ax.plot(
            year_df["month"],
            year_df["per_capita_spend"],
            marker="o",
            markersize=7,
            linewidth=2.4,
            color=year_colors.get(year, "#7F7F7F"),
            label=f"{year}년",
        )

    ax.set_title(
        f"{country} 연도별 월간 1인당 관광소비 추이",
        fontsize=26,
        fontweight="bold",
        pad=24,
    )
    ax.set_xlabel("월", fontsize=14)
    ax.set_ylabel("1인당 관광소비액(원)", fontsize=14)
    ax.set_xticks(range(1, 13), [f"{month}월" for month in range(1, 13)])
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter("{x:,.0f}원"))
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.75)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(
        title="연도",
        loc="upper left",
        bbox_to_anchor=(1.01, 1),
        frameon=False,
        fontsize=11,
        title_fontsize=12,
    )
    fig.tight_layout()

    plt.savefig(
        f"{output_path}/연도별_월간_1인당_관광소비_추이_{country}.png",
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close()

fig, ax = plt.subplots(figsize=(18, 7))
for index, country in enumerate(top_visitor_countries):
    country_df = visitor_df[visitor_df["nationality_nm"].eq(country)]
    ax.plot(
        country_df["date"],
        country_df["tourist_cnt"],
        marker="o",
        markersize=4,
        linewidth=1.8,
        color=colors[index],
        label=country,
    )

ax.set_title("국가별 월별 외국인 방문 추이", fontsize=26, fontweight="bold", pad=34)
ax.text(
    0.5,
    1.01,
    "외국인 방문 건수",
    transform=ax.transAxes,
    ha="center",
    va="bottom",
    fontsize=15,
    color="#666666",
)
ax.set_xlabel("년월", fontsize=14)
ax.set_ylabel("외국인 방문 건수(만 건)", fontsize=14)
ax.set_xticks(all_months)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.tick_params(axis="both", labelsize=12)
ax.tick_params(axis="x", labelrotation=90, labelsize=8)
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8, alpha=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(
    title="국가",
    loc="upper left",
    bbox_to_anchor=(1.01, 1),
    frameon=False,
    fontsize=11,
    title_fontsize=12,
)
fig.tight_layout()

plt.savefig(
    f"{output_path}/국가별_월별_외국인방문건수_추이.png",
    dpi=200,
    bbox_inches="tight",
    facecolor="white",
)
plt.close()

print(f"저장 완료: {output_path}/국가별_월별_관광소비액_추이.png")
print(f"저장 완료: {output_path}/국가별_월별_외국인방문건수_추이.png")
print(f"저장 완료: {output_path}/국가별_월별_1인당_관광소비액_추이.png")
print(f"저장 완료: 국가별 연도 비교 그래프 {len(seasonal_countries)}개")
