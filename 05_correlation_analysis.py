"""
================================================================
FILE        : python/05_correlation_analysis.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Pearson correlation analysis between key numeric
              variables. Covers Task 2 (HP vs MSRP scatter) and
              Task 5 (Cylinders vs MPG scatter + correlation).
              Also produces a full correlation heatmap.
RUN ORDER   : Step 9 - after python/04_market_segmentation.py
NEXT SCRIPT : python/06_dashboard_data_prep.py
OUTPUTS     : outputs/figures/cor_01_cylinders_vs_mpg.png
              outputs/figures/cor_02_hp_vs_msrp.png
              outputs/figures/cor_03_full_heatmap.png
              outputs/figures/cor_04_msrp_correlations_bar.png
              outputs/figures/cor_05_pairplot.png
              outputs/tables/correlation_matrix.csv
              outputs/tables/correlation_with_msrp.csv
================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
from scipy import stats
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
print("  STEP 9 : Correlation Analysis")
print("=" * 60)

df = pd.read_csv(CLEAN_PATH)
print(f"\n  Loaded {len(df):,} rows.\n")


# ------------------------------------------------------------
# 1. TASK 5 : Engine Cylinders vs Highway MPG
# ------------------------------------------------------------
print("[1/5] Task 5 - Cylinders vs Highway MPG...")
cyl_mpg = df[["engine_cylinders", "highway_mpg"]].dropna()
r_cyl, p_cyl = stats.pearsonr(cyl_mpg["engine_cylinders"], cyl_mpg["highway_mpg"])

print(f"       Pearson r = {r_cyl:.4f}")
print(f"       p-value   = {p_cyl:.2e}")
print(f"       Interpretation: {'Strong' if abs(r_cyl) > 0.6 else 'Moderate'} "
      f"{'negative' if r_cyl < 0 else 'positive'} correlation")

slope_c, intercept_c = np.polyfit(
    cyl_mpg["engine_cylinders"], cyl_mpg["highway_mpg"], 1
)
x_range_c = np.linspace(
    cyl_mpg["engine_cylinders"].min(),
    cyl_mpg["engine_cylinders"].max(), 100
)

avg_by_cyl = (cyl_mpg.groupby("engine_cylinders")["highway_mpg"]
              .mean().reset_index())

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(cyl_mpg["engine_cylinders"], cyl_mpg["highway_mpg"],
           alpha=0.18, s=14, color="#4393c3", label="Individual cars")
ax.plot(x_range_c, slope_c * x_range_c + intercept_c,
        color="#d73027", linewidth=2.2,
        label=f"Trendline  (r = {r_cyl:.3f})")
ax.plot(avg_by_cyl["engine_cylinders"], avg_by_cyl["highway_mpg"],
        color="#1a9850", linestyle="--", linewidth=1.5,
        marker="s", markersize=7, label="Avg MPG per cylinder count")
ax.set_title(
    f"Task 5A : Engine Cylinders vs Highway MPG\n"
    f"Pearson r = {r_cyl:.4f}  |  p = {p_cyl:.2e}",
    fontsize=13, fontweight="bold"
)
ax.set_xlabel("Number of Cylinders")
ax.set_ylabel("Highway MPG")
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/cor_01_cylinders_vs_mpg.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: cor_01_cylinders_vs_mpg.png")


# ------------------------------------------------------------
# 2. TASK 2 : Engine HP vs MSRP
# ------------------------------------------------------------
print("\n[2/5] Task 2 - Engine HP vs MSRP...")
hp_msrp = df[["engine_hp", "msrp"]].dropna()
r_hp, p_hp = stats.pearsonr(hp_msrp["engine_hp"], hp_msrp["msrp"])

print(f"       Pearson r = {r_hp:.4f}")
print(f"       p-value   = {p_hp:.2e}")
print(f"       Interpretation: {'Strong' if abs(r_hp) > 0.6 else 'Moderate'} "
      f"{'positive' if r_hp > 0 else 'negative'} correlation")

slope_h, intercept_h = np.polyfit(hp_msrp["engine_hp"], hp_msrp["msrp"], 1)
x_range_h = np.linspace(
    hp_msrp["engine_hp"].min(), hp_msrp["engine_hp"].max(), 100
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(hp_msrp["engine_hp"], hp_msrp["msrp"],
           alpha=0.18, s=14, color="#f46d43", label="Individual cars")
ax.plot(x_range_h, slope_h * x_range_h + intercept_h,
        color="#313695", linewidth=2.2,
        label=f"Trendline  (r = {r_hp:.3f})")
ax.set_title(
    f"Task 2 : Engine HP vs MSRP\n"
    f"Pearson r = {r_hp:.4f}  |  p = {p_hp:.2e}",
    fontsize=13, fontweight="bold"
)
ax.set_xlabel("Engine Horsepower (HP)")
ax.set_ylabel("MSRP ($)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax.text(0.05, 0.93,
        f"Each +1 HP = approx +${slope_h:,.0f} in price",
        transform=ax.transAxes, fontsize=10, color="#313695",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/cor_02_hp_vs_msrp.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: cor_02_hp_vs_msrp.png")


# ------------------------------------------------------------
# 3. FULL CORRELATION MATRIX
# ------------------------------------------------------------
print("\n[3/5] Building full correlation matrix...")
NUMERIC_COLS = [
    "engine_hp", "engine_cylinders", "highway_mpg", "city_mpg",
    "popularity", "number_of_doors", "year", "msrp",
    "mpg_avg", "hp_per_dollar"
]
corr_df = df[NUMERIC_COLS].corr().round(3)
corr_df.to_csv(f"{TAB_DIR}/correlation_matrix.csv")

msrp_corr = (corr_df["msrp"]
             .drop("msrp")
             .sort_values(key=abs, ascending=False)
             .reset_index())
msrp_corr.columns = ["feature", "correlation_with_msrp"]
msrp_corr.to_csv(f"{TAB_DIR}/correlation_with_msrp.csv", index=False)

print("       Correlations with MSRP (sorted by |r|):")
print(msrp_corr.to_string(index=False))

mask = np.triu(np.ones_like(corr_df, dtype=bool))
fig, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(
    corr_df, mask=mask, annot=True, fmt=".2f",
    cmap="RdYlGn", center=0, vmin=-1, vmax=1,
    linewidths=0.5, linecolor="white",
    annot_kws={"size": 9}, ax=ax
)
ax.set_title("Correlation Heatmap - All Numeric Features",
             fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/cor_03_full_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: cor_03_full_heatmap.png")


# ------------------------------------------------------------
# 4. BAR CHART - Correlations with MSRP
# ------------------------------------------------------------
print("\n[4/5] Plotting correlations with MSRP bar chart...")
msrp_corr_sorted = msrp_corr.sort_values("correlation_with_msrp", ascending=True)
bar_colors = ["#d73027" if v > 0 else "#4575b4"
              for v in msrp_corr_sorted["correlation_with_msrp"]]

fig, ax = plt.subplots(figsize=(10, 7))
ax.barh(msrp_corr_sorted["feature"],
        msrp_corr_sorted["correlation_with_msrp"],
        color=bar_colors, edgecolor="white", linewidth=0.5)
ax.axvline(x=0, color="black", linewidth=0.9, linestyle="--")
ax.set_title("Pearson Correlation of All Features with MSRP",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Pearson Correlation Coefficient (r)")
ax.set_xlim(-1.1, 1.1)
for i, (val, feat) in enumerate(zip(
        msrp_corr_sorted["correlation_with_msrp"],
        msrp_corr_sorted["feature"])):
    xpos = val + (0.02 if val >= 0 else -0.02)
    ha   = "left" if val >= 0 else "right"
    ax.text(xpos, i, f"{val:.3f}", va="center", ha=ha, fontsize=9)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/cor_04_msrp_correlations_bar.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: cor_04_msrp_correlations_bar.png")


# ------------------------------------------------------------
# 5. PAIRPLOT - Key Variables (sampled for speed)
# ------------------------------------------------------------
print("\n[5/5] Generating pairplot (sampled 1,500 rows)...")
PAIR_COLS  = ["engine_hp", "engine_cylinders", "highway_mpg", "msrp"]
sample_df  = df[PAIR_COLS + ["price_tier"]].dropna().sample(
    n=min(1500, len(df)), random_state=42
)
tier_palette = {
    "Budget"      : "#74c476",
    "Mid-Range"   : "#41ab5d",
    "Premium"     : "#238b45",
    "Luxury"      : "#006d2c",
    "Ultra-Luxury": "#00441b"
}
g = sns.pairplot(
    sample_df,
    hue="price_tier",
    palette=tier_palette,
    diag_kind="kde",
    plot_kws={"alpha": 0.3, "s": 15},
    height=2.5
)
g.fig.suptitle("Pairplot - Key Features coloured by Price Tier",
               y=1.02, fontsize=13, fontweight="bold")
plt.savefig(f"{FIG_DIR}/cor_05_pairplot.png", dpi=120, bbox_inches="tight")
plt.close()
print("        Saved: cor_05_pairplot.png")


# -- Summary --------------------------------------------------
print("\n" + "=" * 60)
print("  CORRELATION ANALYSIS COMPLETE")
print("=" * 60)
print(f"\n  Key findings:")
print(f"    engine_hp vs MSRP        : r = {r_hp:.4f}  (strong positive)")
print(f"    cylinders vs highway_mpg : r = {r_cyl:.4f}  (strong negative)")
print(f"\n  Full matrix -> {TAB_DIR}/correlation_matrix.csv")
print("\n  Next step -> python/06_dashboard_data_prep.py")
