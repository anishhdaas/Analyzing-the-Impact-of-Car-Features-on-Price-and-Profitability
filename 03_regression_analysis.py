"""
================================================================
FILE        : python/03_regression_analysis.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Multiple Linear Regression to identify which car
              features most strongly predict MSRP.
              Answers Analytical Task 3 from the project brief.
RUN ORDER   : Step 7 - after python/02_eda_visualization.py
NEXT SCRIPT : python/04_market_segmentation.py
OUTPUTS     : outputs/figures/reg_01_coefficients.png
              outputs/figures/reg_02_actual_vs_predicted.png
              outputs/figures/reg_03_residuals.png
              outputs/tables/regression_coefficients.csv
              outputs/tables/regression_summary.csv
================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler
from matplotlib.patches import Patch
import os
import warnings

warnings.filterwarnings("ignore")

# -- Config ---------------------------------------------------
CLEAN_PATH = "data/cleaned/car_data_cleaned.csv"
FIG_DIR    = "outputs/figures"
TAB_DIR    = "outputs/tables"
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TAB_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", font_scale=1.1)

print("=" * 60)
print("  STEP 7 : Multiple Linear Regression Analysis")
print("=" * 60)

df = pd.read_csv(CLEAN_PATH)
print(f"\n  Loaded {len(df):,} rows.\n")


# ------------------------------------------------------------
# 1. FEATURE ENGINEERING
#    Numeric  : as-is from cleaned dataset
#    Encoded  : binary flags from key categoricals
# ------------------------------------------------------------
print("[1/6] Engineering features...")

df["is_luxury"]        = df["market_category"].str.contains("Luxury",        na=False).astype(int)
df["is_performance"]   = df["market_category"].str.contains("Performance",   na=False).astype(int)
df["is_crossover"]     = df["market_category"].str.contains("Crossover",     na=False).astype(int)
df["is_exotic"]        = df["market_category"].str.contains("Exotic",        na=False).astype(int)
df["is_hybrid"]        = df["market_category"].str.contains("Hybrid",        na=False).astype(int)
df["is_factory_tuner"] = df["market_category"].str.contains("Factory Tuner", na=False).astype(int)
df["is_automatic"]     = (df["transmission_type"] == "AUTOMATIC").astype(int)
df["is_awd"]           = df["driven_wheels"].str.contains("all wheel",  case=False, na=False).astype(int)
df["is_rwd"]           = df["driven_wheels"].str.contains("rear wheel", case=False, na=False).astype(int)
df["is_large"]         = (df["vehicle_size"] == "Large").astype(int)
df["is_compact"]       = (df["vehicle_size"] == "Compact").astype(int)

NUMERIC_FEATURES = [
    "engine_hp", "engine_cylinders", "highway_mpg",
    "city_mpg", "popularity", "number_of_doors", "year"
]
ENCODED_FEATURES = [
    "is_luxury", "is_performance", "is_crossover",
    "is_exotic", "is_hybrid", "is_factory_tuner",
    "is_automatic", "is_awd", "is_rwd",
    "is_large", "is_compact"
]
ALL_FEATURES = NUMERIC_FEATURES + ENCODED_FEATURES
TARGET = "msrp"

print(f"       Numeric features : {len(NUMERIC_FEATURES)}")
print(f"       Encoded features : {len(ENCODED_FEATURES)}")
print(f"       Total features   : {len(ALL_FEATURES)}")


# ------------------------------------------------------------
# 2. PREPARE DATA
# ------------------------------------------------------------
print("\n[2/6] Preparing model data...")
model_df = df[ALL_FEATURES + [TARGET]].dropna()
X = model_df[ALL_FEATURES]
y = model_df[TARGET]
print(f"       Model dataset shape: {X.shape[0]:,} rows x {X.shape[1]} features")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
print(f"       Train set : {len(X_train):,} rows")
print(f"       Test set  : {len(X_test):,} rows")


# ------------------------------------------------------------
# 3. STANDARDISE FEATURES
# ------------------------------------------------------------
print("\n[3/6] Standardising features (StandardScaler)...")
scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)


# ------------------------------------------------------------
# 4. FIT MODEL AND EVALUATE
# ------------------------------------------------------------
print("\n[4/6] Fitting Linear Regression model...")
reg    = LinearRegression()
reg.fit(X_train_sc, y_train)
y_pred = reg.predict(X_test_sc)

r2   = r2_score(y_test, y_pred)
mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mape = (np.abs((y_test - y_pred) / y_test)).mean() * 100

cv_scores = cross_val_score(reg, scaler.transform(X), y, cv=5, scoring="r2")

print(f"\n       Model Performance:")
print(f"         R2 Score          : {r2:.4f}  ({r2*100:.1f}% variance explained)")
print(f"         Mean Abs Error    : ${mae:>10,.0f}")
print(f"         Root Mean Sq Err  : ${rmse:>10,.0f}")
print(f"         Mean Abs Pct Error: {mape:.2f}%")
print(f"         Cross-Val R2 (5k) : {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}")


# ------------------------------------------------------------
# 5. COEFFICIENT TABLE
# ------------------------------------------------------------
print("\n[5/6] Building coefficient table...")
coef_df = pd.DataFrame({
    "feature"    : ALL_FEATURES,
    "coefficient": reg.coef_,
    "abs_coef"   : np.abs(reg.coef_)
}).sort_values("coefficient", ascending=False)

print("\n       Feature Importance (ranked by coefficient):")
print(coef_df[["feature", "coefficient"]].to_string(index=False))

coef_df.to_csv(f"{TAB_DIR}/regression_coefficients.csv", index=False)

summary = pd.DataFrame({
    "metric": ["R2", "MAE", "RMSE", "MAPE", "CV_R2_mean", "CV_R2_std"],
    "value" : [round(r2, 4), round(mae, 2), round(rmse, 2),
               round(mape, 4), round(cv_scores.mean(), 4), round(cv_scores.std(), 4)]
})
summary.to_csv(f"{TAB_DIR}/regression_summary.csv", index=False)


# ------------------------------------------------------------
# 6. CHARTS
# ------------------------------------------------------------
print("\n[6/6] Generating charts...")

# Chart 1 : Coefficient Bar Chart (Task 3)
coef_sorted = coef_df.sort_values("coefficient", ascending=True)
colors = ["#d73027" if c > 0 else "#4575b4" for c in coef_sorted["coefficient"]]

fig, ax = plt.subplots(figsize=(11, 8))
bars = ax.barh(coef_sorted["feature"], coef_sorted["coefficient"],
               color=colors, edgecolor="white", linewidth=0.5)
ax.axvline(x=0, color="black", linewidth=0.9, linestyle="--")
ax.set_title(
    f"Task 3 : Feature Importance - Standardised Regression Coefficients\n"
    f"R2 = {r2:.3f}  |  RMSE = ${rmse:,.0f}  |  MAE = ${mae:,.0f}",
    fontsize=12, fontweight="bold"
)
ax.set_xlabel("Standardised Coefficient Value")
ax.set_ylabel("Feature")
for bar, val in zip(bars, coef_sorted["coefficient"]):
    xpos = bar.get_width() + (300 if val >= 0 else -300)
    ha   = "left" if val >= 0 else "right"
    ax.text(xpos, bar.get_y() + bar.get_height() / 2,
            f"{val:,.0f}", va="center", ha=ha, fontsize=8.5)
legend_handles = [
    Patch(color="#d73027", label="Positive effect on MSRP"),
    Patch(color="#4575b4", label="Negative effect on MSRP")
]
ax.legend(handles=legend_handles, loc="lower right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/reg_01_coefficients.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: reg_01_coefficients.png")

# Chart 2 : Actual vs Predicted Scatter
fig, ax = plt.subplots(figsize=(8, 7))
ax.scatter(y_test, y_pred, alpha=0.25, s=12, color="#2c7bb6", label="Predictions")
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect Fit")
ax.set_title("Actual vs Predicted MSRP", fontsize=13, fontweight="bold")
ax.set_xlabel("Actual MSRP ($)")
ax.set_ylabel("Predicted MSRP ($)")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax.text(0.05, 0.93, f"R2 = {r2:.3f}", transform=ax.transAxes,
        fontsize=11, color="darkgreen", fontweight="bold")
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/reg_02_actual_vs_predicted.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: reg_02_actual_vs_predicted.png")

# Chart 3 : Residuals Distribution
residuals = y_test - y_pred
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Residual Analysis", fontsize=13, fontweight="bold")

axes[0].hist(residuals, bins=60, color="#74add1", edgecolor="white", linewidth=0.4)
axes[0].axvline(0, color="red", linestyle="--", linewidth=1.2)
axes[0].set_title("Residuals Distribution")
axes[0].set_xlabel("Residual ($)")
axes[0].set_ylabel("Count")

axes[1].scatter(y_pred, residuals, alpha=0.2, s=10, color="#4393c3")
axes[1].axhline(0, color="red", linestyle="--", linewidth=1.2)
axes[1].set_title("Residuals vs Fitted Values")
axes[1].set_xlabel("Fitted (Predicted) MSRP ($)")
axes[1].set_ylabel("Residual ($)")
axes[1].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/reg_03_residuals.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: reg_03_residuals.png")


# -- Summary --------------------------------------------------
print("\n" + "=" * 60)
print("  REGRESSION COMPLETE")
print("=" * 60)
print(f"  R2   = {r2:.4f}  -> model explains {r2*100:.1f}% of MSRP variance")
print(f"  MAE  = ${mae:,.0f}")
print(f"  RMSE = ${rmse:,.0f}")
print(f"\n  Top 3 positive drivers of price:")
for _, row in coef_df.nlargest(3, "coefficient")[["feature", "coefficient"]].iterrows():
    print(f"    {row['feature']:25s}  coef = {row['coefficient']:>10,.0f}")
print(f"\n  Top 3 negative drivers of price:")
for _, row in coef_df.nsmallest(3, "coefficient")[["feature", "coefficient"]].iterrows():
    print(f"    {row['feature']:25s}  coef = {row['coefficient']:>10,.0f}")
print("\n  Next step -> python/04_market_segmentation.py")
