import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.inspection import permutation_importance


# 1. 데이터 불러오기
file_path = "C:/Users/user/Downloads/회귀분석용_최종데이터.xlsx"
df = pd.read_excel(file_path)


# 2. 타깃 생성
# 관광방문자 = 외지인 + 외국인

df["예측대상월_관광방문자수"] = (
    pd.to_numeric(df["예측대상월_외지인방문자수"], errors="coerce")
    + pd.to_numeric(df["예측대상월_외국인방문자수"], errors="coerce")
)

df["전월_관광방문자수"] = (
    pd.to_numeric(df["전월_외지인방문자수"], errors="coerce")
    + pd.to_numeric(df["전월_외국인방문자수"], errors="coerce")
)

df["관광방문자_성장률(%)"] = (
    (df["예측대상월_관광방문자수"] - df["전월_관광방문자수"])
    / df["전월_관광방문자수"]
    * 100
)


# 3. 변수 설정

target = "관광방문자_성장률(%)"

features = [
    "전월_지역검색건수",
    "전월_대중교통이용인원",
    "전월_관광지출_외지인",
    "전월_관광지출_외국인",
    "전월_숙박업소수",
    "전월_음식점수",
    "전월_총인구수",
    "전월_강수일수",
    "예측대상월_지역축제개최일수",
    "예측대상월_지역축제수",
    "예측대상월_한국공휴일수",
    "예측대상월_해외총공휴일수",
    "전월_외지인방문비율",
    "전월_외국인방문비율",
    "월_sin",
    "월_cos"
]


# 4. 분석 데이터 정리

model_df = df[
    ["예측대상연월", "구군", target] + features
].copy()

for col in features + [target]:
    model_df[col] = pd.to_numeric(model_df[col], errors="coerce")

model_df = model_df.dropna(
    subset=features + [target]
).reset_index(drop=True)

print("전체 데이터:", len(model_df))


# 5. Train / Test 랜덤 분할

X = model_df[features]
y = model_df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    shuffle=True
)

print("Train:", X_train.shape)
print("Test :", X_test.shape)


# 6. 모델 비교

models = {
    "Linear Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ]),

    "Ridge": Pipeline([
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=1.0))
    ]),

    "RandomForest": RandomForestRegressor(
        n_estimators=500,
        random_state=42,
        n_jobs=-1
    )
}

results = []

for name, model in models.items():

    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    results.append({
        "모델": name,
        "MAE": mean_absolute_error(y_test, pred),
        "RMSE": np.sqrt(mean_squared_error(y_test, pred)),
        "R²": r2_score(y_test, pred)
    })

result_df = pd.DataFrame(results).sort_values(
    "R²",
    ascending=False
).reset_index(drop=True)

print("\n===== 모델 성능 비교 =====")
print(result_df.to_string(index=False))


# 7. RandomForest 튜닝

param_grid = {
    "n_estimators": [300],
    "max_depth": [5, 8, 10, 12, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4, 6],
    "max_features": ["sqrt", 0.7, 1.0]
}

grid = list(ParameterGrid(param_grid))

tuning_results = []

for i, params in enumerate(grid, start=1):

    model = RandomForestRegressor(
        random_state=42,
        n_jobs=-1,
        **params
    )

    model.fit(X_train, y_train)

    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    tuning_results.append({
        **params,
        "Train_R2": train_r2,
        "Test_R2": test_r2,
        "Test_MAE": mean_absolute_error(y_test, test_pred),
        "Test_RMSE": np.sqrt(mean_squared_error(y_test, test_pred)),
        "과적합차이": train_r2 - test_r2
    })

    if i % 20 == 0:
        print(f"{i} / {len(grid)} 완료")

tuning_df = pd.DataFrame(tuning_results).sort_values(
    ["Test_R2", "과적합차이"],
    ascending=[False, True]
).reset_index(drop=True)

print("\n===== 튜닝 상위 20개 =====")
print(tuning_df.head(20).to_string(index=False))


# 8. 최종 모델

best_rf = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1
)

best_rf.fit(X_train, y_train)

train_pred = best_rf.predict(X_train)
test_pred = best_rf.predict(X_test)

train_r2 = r2_score(y_train, train_pred)
test_r2 = r2_score(y_test, test_pred)
test_mae = mean_absolute_error(y_test, test_pred)
test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))

print("\n===== 최종 모델 =====")
print("Train R²:", round(train_r2, 3))
print("Test R² :", round(test_r2, 3))
print("Test MAE :", round(test_mae, 3))
print("Test RMSE:", round(test_rmse, 3))


# 9. RandomForest 변수 중요도

importance_df = pd.DataFrame({
    "변수": features,
    "RF_중요도": best_rf.feature_importances_
}).sort_values(
    "RF_중요도",
    ascending=False
).reset_index(drop=True)

print("\n===== RF 변수 중요도 =====")
print(importance_df.to_string(index=False))


# 10. Permutation Importance

perm = permutation_importance(
    best_rf,
    X_test,
    y_test,
    scoring="r2",
    n_repeats=30,
    random_state=42,
    n_jobs=-1
)

perm_df = pd.DataFrame({
    "변수": features,
    "Permutation_중요도": perm.importances_mean,
    "표준편차": perm.importances_std
}).sort_values(
    "Permutation_중요도",
    ascending=False
).reset_index(drop=True)

print("\n===== Permutation Importance =====")
print(perm_df.to_string(index=False))


# 11. 실제값 / 예측값

prediction_df = model_df.loc[
    X_test.index,
    ["예측대상연월", "구군", target]
].copy()

prediction_df["예측성장률(%)"] = test_pred
prediction_df["오차"] = (
    prediction_df[target] - prediction_df["예측성장률(%)"]
)
prediction_df["절대오차"] = prediction_df["오차"].abs()

prediction_df = prediction_df.sort_values(
    ["예측대상연월", "구군"]
).reset_index(drop=True)


#폰트 설정
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

%matplotlib auto
# 12. 실제값 vs 예측값

plt.figure(figsize=(8, 8))

plt.scatter(
    y_test,
    test_pred,
    alpha=0.7
)

min_val = min(y_test.min(), test_pred.min())
max_val = max(y_test.max(), test_pred.max())

plt.plot(
    [min_val, max_val],
    [min_val, max_val],
    linestyle="--"
)

plt.xlabel("실제 관광방문자 성장률 (%)")
plt.ylabel("예측 관광방문자 성장률 (%)")
plt.title(f"실제값 vs 예측값 (R² = {test_r2:.3f})")
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# 13. RF 변수 중요도 TOP 10

plot_df = importance_df.head(10).sort_values("RF_중요도")

plt.figure(figsize=(9, 6))
plt.barh(plot_df["변수"], plot_df["RF_중요도"])
plt.xlabel("Feature Importance")
plt.title("RandomForest 변수 중요도 TOP 10")
plt.tight_layout()
plt.show()


# 14. Permutation Importance TOP 10

perm_plot = perm_df.head(10).sort_values("Permutation_중요도")

plt.figure(figsize=(9, 6))
plt.barh(
    perm_plot["변수"],
    perm_plot["Permutation_중요도"]
)
plt.xlabel("Permutation Importance")
plt.title("Permutation Importance TOP 10")
plt.tight_layout()
plt.show()


# 15. 결과 저장

with pd.ExcelWriter(
    "회귀분석_랜덤분할_최종결과.xlsx",
    engine="openpyxl"
) as writer:

    result_df.to_excel(
        writer,
        sheet_name="모델비교",
        index=False
    )

    tuning_df.to_excel(
        writer,
        sheet_name="튜닝결과",
        index=False
    )

    importance_df.to_excel(
        writer,
        sheet_name="RF변수중요도",
        index=False
    )

    perm_df.to_excel(
        writer,
        sheet_name="Permutation중요도",
        index=False
    )

    prediction_df.to_excel(
        writer,
        sheet_name="실제값예측값",
        index=False
    )

print("\n저장 완료")
