import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


# ==================================================
# 0. 설정
# ==================================================

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

base_path = "C:/Users/user/Desktop/pj2.data/cluster analysis/"


# ==================================================
# 1. 데이터 불러오기
# ==================================================

tour = pd.read_excel(
    base_path + "부산_구군별_관광지.xlsx"
)

visit_ratio = pd.read_excel(
    base_path + "부산_구군별_방문자비율.xlsx"
)

spending = pd.read_excel(
    base_path + "부산_구군별_관광소비.xlsx"
)

accommodation = pd.read_excel(
    base_path + "부산_구군별_숙박업소수.xlsx"
)

restaurant = pd.read_excel(
    base_path + "부산_구군별_음식점수.xlsx"
)

stay_ratio = pd.read_excel(
    base_path + "부산_구군별_월별_숙박자비율.xlsx"
)

stay_time = pd.read_excel(
    base_path + "부산_구군별_월별_평균체류시간.xlsx"
)

visitors = pd.read_excel(
    base_path + "부산_구군별_월별_순방문자수.xlsx"
)

bus_stop = pd.read_csv(
    base_path + "부산_구군별_대중교통접근성.csv",
    encoding="cp949"
)

additional = pd.read_excel(
    base_path + "부산_군집분석용_추가지표.xlsx"
)

# ==================================================
# 2. 숙박자 비율 구군별 평균
# ==================================================

stay_ratio_avg = (
    stay_ratio
    .groupby("구군", as_index=False)["숙박자 비율(%)"]
    .mean()
    .rename(
        columns={
            "숙박자 비율(%)": "평균숙박자비율"
        }
    )
)


# ==================================================
# 3. 컬럼명 정리
# ==================================================

visit_ratio = visit_ratio.rename(
    columns={
        "외지인 방문 비율": "외지인방문비율",
        "외국인 방문 비율": "외국인방문비율"
    }
)

spending = spending.rename(
    columns={
        "1인당 관광소비(원자료단위/방문자)": "1인당관광소비"
    }
)

bus_stop = bus_stop[
    ["시군구", "공급도"]
].copy()

bus_stop = bus_stop.rename(
    columns={
        "시군구": "구군",
        "공급도": "정류장공급도"
    }
)

tour = tour[
    [
        "구군",
        "관광지수"
    ]
].copy()


# ==================================================
# 4. 데이터 병합
# ==================================================

cluster_df = tour.copy()

merge_list = [
    visit_ratio[
        [
            "구군",
            "외지인방문비율",
            "외국인방문비율"
        ]
    ],

    spending[
        [
            "구군",
            "1인당관광소비"
        ]
    ],

    accommodation,
    stay_ratio_avg,
    bus_stop
]

for data in merge_list:

    cluster_df = cluster_df.merge(
        data,
        on="구군",
        how="left"
    )


cluster_df = cluster_df.merge(
    additional,
    on="구군",
    how="left"
)


# ==================================================
# 5. 최종 9개 변수
# ==================================================

features = [
    "관광지수",
    "1인당관광소비",
    "외지인방문비율",
    "외국인방문비율",
    "평균숙박자비율",
    "숙박업소수",
    "정류장공급도",
    "숙박소비비중",
    "수도권비중_외지인중"
]

print("\n===== 최종 9개 변수 =====")
print(features)


# ==================================================
# 6. 숫자형 변환
# ==================================================

for col in features:

    cluster_df[col] = pd.to_numeric(
        cluster_df[col],
        errors="coerce"
    )


# ==================================================
# 7. 결측치
# ==================================================

print("\n===== 결측치 =====")

print(
    cluster_df[
        features
    ].isna().sum()
)


# ==================================================
# 8. 상관관계
# ==================================================

corr = cluster_df[
    features
].corr()

print("\n===== 상관관계 =====")
print(corr.round(3))


high_corr = []

for i in range(len(corr.columns)):

    for j in range(i + 1, len(corr.columns)):

        value = corr.iloc[i, j]

        if abs(value) >= 0.8:

            high_corr.append({
                "변수1": corr.columns[i],
                "변수2": corr.columns[j],
                "상관계수": value
            })


high_corr_df = pd.DataFrame(
    high_corr
)

print("\n===== |상관계수| 0.8 이상 =====")
print(high_corr_df)


# ==================================================
# 9. 분석 데이터
# ==================================================

analysis_df = cluster_df[
    ["구군"] + features
].copy()

analysis_df = (
    analysis_df
    .dropna()
    .reset_index(drop=True)
)

print(
    "\n분석 지역 수:",
    len(analysis_df)
)


# ==================================================
# 10. 표준화
# ==================================================

X = analysis_df[features]

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


scaled_df = pd.DataFrame(
    X_scaled,
    columns=features
)

scaled_df.insert(
    0,
    "구군",
    analysis_df["구군"]
)


# ==================================================
# 11. k=2~6 비교
# ==================================================

k_results = []

for k in range(2, 7):

    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=20
    )

    labels = kmeans.fit_predict(
        X_scaled
    )

    silhouette = silhouette_score(
        X_scaled,
        labels
    )

    k_results.append({
        "군집수": k,
        "Silhouette": silhouette,
        "Inertia": kmeans.inertia_
    })


k_result_df = pd.DataFrame(
    k_results
)

print("\n===== 군집 수 비교 =====")
print(k_result_df)


# ==================================================
# 12. Silhouette 그래프
# ==================================================

plt.figure(figsize=(7, 5))

plt.plot(
    k_result_df["군집수"],
    k_result_df["Silhouette"],
    marker="o"
)

plt.xlabel("군집 수 (k)")
plt.ylabel("Silhouette Score")
plt.title("군집 수별 Silhouette Score")

plt.xticks(
    k_result_df["군집수"]
)

plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()


# ==================================================
# 13. Elbow 그래프
# ==================================================

plt.figure(figsize=(7, 5))

plt.plot(
    k_result_df["군집수"],
    k_result_df["Inertia"],
    marker="o"
)

plt.xlabel("군집 수 (k)")
plt.ylabel("Inertia")
plt.title("KMeans Elbow Method")

plt.xticks(
    k_result_df["군집수"]
)

plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()


# ==================================================
# 14. 실루엣 최고 k
# ==================================================

best_k = int(
    k_result_df.loc[
        k_result_df["Silhouette"].idxmax(),
        "군집수"
    ]
)

print(
    "\n실루엣 기준 최적 군집 수:",
    best_k
)


# ==================================================
# 15. 최종 KMeans
# ==================================================

kmeans = KMeans(
    n_clusters=best_k,
    random_state=42,
    n_init=20
)

analysis_df["군집"] = (
    kmeans.fit_predict(
        X_scaled
    )
    + 1
)


# ==================================================
# 16. 구군별 군집
# ==================================================

print("\n===== 구군별 군집 =====")

print(
    analysis_df[
        ["구군", "군집"]
    ]
    .sort_values(
        ["군집", "구군"]
    )
    .to_string(index=False)
)


for cluster in sorted(
    analysis_df["군집"].unique()
):

    regions = analysis_df.loc[
        analysis_df["군집"] == cluster,
        "구군"
    ].tolist()

    print(
        f"\n군집 {cluster}:",
        ", ".join(regions)
    )


# ==================================================
# 17. 군집별 원자료 평균
# ==================================================

cluster_mean = (
    analysis_df
    .groupby("군집")[features]
    .mean()
    .round(3)
)

print(
    "\n===== 군집별 평균 ====="
)

print(cluster_mean)


# ==================================================
# 18. 군집별 표준화 평균
# ==================================================

profile_df = pd.DataFrame(
    X_scaled,
    columns=features
)

profile_df["군집"] = (
    analysis_df["군집"].values
)

cluster_profile = (
    profile_df
    .groupby("군집")[features]
    .mean()
    .round(3)
)

print(
    "\n===== 군집별 표준화 평균 ====="
)

print(cluster_profile)


# ==================================================
# 19. PCA
# ==================================================

pca = PCA(
    n_components=2
)

pca_result = pca.fit_transform(
    X_scaled
)

analysis_df["PCA1"] = (
    pca_result[:, 0]
)

analysis_df["PCA2"] = (
    pca_result[:, 1]
)


print(
    "\nPCA 설명력:",
    pca.explained_variance_ratio_
)

print(
    "PCA 누적 설명력:",
    pca.explained_variance_ratio_.sum()
)


# ==================================================
# 20. PCA 시각화
# ==================================================

plt.figure(
    figsize=(9, 7)
)

for cluster in sorted(
    analysis_df["군집"].unique()
):

    temp = analysis_df[
        analysis_df["군집"] == cluster
    ]

    plt.scatter(
        temp["PCA1"],
        temp["PCA2"],
        s=100,
        label=f"군집 {cluster}"
    )


for _, row in analysis_df.iterrows():

    plt.text(
        row["PCA1"] + 0.05,
        row["PCA2"] + 0.05,
        row["구군"],
        fontsize=9
    )


plt.xlabel("PCA 1")
plt.ylabel("PCA 2")

plt.title(
    "부산 16개 구·군 관광 유형 군집"
)

plt.legend()
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()


# ==================================================
# 21. 군집 프로파일 그래프
# ==================================================

cluster_profile.T.plot(
    kind="bar",
    figsize=(13, 7)
)

plt.axhline(
    0,
    linestyle="--"
)

plt.ylabel("표준화 평균")
plt.xlabel("변수")

plt.title(
    "군집별 관광 특성 비교"
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()


# ==================================================
# 22. 결과 저장
# ==================================================

with pd.ExcelWriter(
    base_path + "부산_관광지역_군집분석_최종_9변수.xlsx",
    engine="openpyxl"
) as writer:

    analysis_df.to_excel(
        writer,
        sheet_name="구군별군집",
        index=False
    )

    k_result_df.to_excel(
        writer,
        sheet_name="군집수비교",
        index=False
    )

    high_corr_df.to_excel(
        writer,
        sheet_name="높은상관관계",
        index=False
    )

    corr.to_excel(
        writer,
        sheet_name="상관계수"
    )

    scaled_df.to_excel(
        writer,
        sheet_name="표준화데이터",
        index=False
    )

    cluster_mean.to_excel(
        writer,
        sheet_name="군집별평균"
    )

    cluster_profile.to_excel(
        writer,
        sheet_name="군집별표준화평균"
    )
