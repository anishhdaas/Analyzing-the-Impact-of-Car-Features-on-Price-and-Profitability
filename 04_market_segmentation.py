"""
================================================================
FILE        : python/04_market_segmentation.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Analyse market category and brand-level segments.
              Produces combo chart (Task 1), brand MSRP charts
              (Task 4), and a brand x body-style MSRP heatmap.
RUN ORDER   : Step 8 - after python/03_regression_analysis.py
NEXT SCRIPT : python/05_correlation_analysis.py
OUTPUTS     : outputs/figures/seg_01_market_category_combo.png
              outputs/figures/seg_02_top_brands_msrp.png
              outputs/figures/seg_03_brand_style_heatmap.png
              outputs/figures/seg_04_popularity_vs_price.png
              outputs/tables/task1_market_category.csv
              outputs/tables/task4_brand_avg_msrp.csv
================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
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
print("  STEP 8 : Market Segmentation Analysis")
print("=" * 60)

df = pd.read_csv(CLEAN_PATH)
print(f"\n  Loaded {len(df):,} rows.\n")


# ------------------------------------------------------------
# 1. MARKET CATEGORY ANALYSIS - Task 1
#    Combo chart: bar = model count, line = avg popularity
# ------------------------------------------------------------
print("[1/4] Analysing market categories (Task 1)...")
cat_df = (
    df.groupby("market_category")
    .agg(
        num_models     = ("model",      "count"),
        avg_popularity = ("popularity", "mean"),
        avg_msrp       = ("msrp",       "mean"),
        avg_hp         = ("engine_hp",  "mean")
    )
    .reset_index()
    .sort_values("avg_popularity", ascending=False)
)
cat_df[["avg_popularity", "avg_msrp", "avg_hp"]] = \
    cat_df[["avg_popularity", "avg_msrp", "avg_hp"]].round(1)

cat_df.to_csv(f"{TAB_DIR}/task1_market_category.csv", index=False)
print(f"       Saved: task1_market_category.csv  ({len(cat_df)} categories)")

top_cat = cat_df.head(15).sort_values("num_models", ascending=False)

fig, ax1 = plt.subplots(figsize=(16, 7))
x = range(len(top_cat))
ax1.bar(x, top_cat["num_models"],
        color="#4393c3", alpha=0.8, label="Number of Models")
ax1.set_xticks(x)
ax1.set_xticklabels(top_cat["market_category"],
                    rotation=40, ha="right", fontsize=9)
ax1.set_xlabel("Market Category")
ax1.set_ylabel("Number of Models", color="#4393c3")
ax1.tick_params(axis="y", labelcolor="#4393c3")

ax2 = ax1.twinx()
ax2.plot(x, top_cat["avg_popularity"], color="#d73027",
         marker="o", linewidth=2.2, markersize=6, label="Avg Popularity")
ax2.set_ylabel("Average Popularity Score", color="#d73027")
ax2.tick_params(axis="y", labelcolor="#d73027")

fig.suptitle(
    "Task 1 : Market Category - Number of Models vs Average Popularity",
    fontsize=13, fontweight="bold"
)
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/seg_01_market_category_combo.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: seg_01_market_category_combo.png")


# ------------------------------------------------------------
# 2. BRAND AVERAGE MSRP - Task 4
#    Horizontal bar chart - top 25 brands by avg MSRP
# ------------------------------------------------------------
print("\n[2/4] Analysing brand pricing (Task 4)...")
brand_df = (
    df.groupby("make")
    .agg(
        avg_msrp       = ("msrp",        "mean"),
        min_msrp       = ("msrp",        "min"),
        max_msrp       = ("msrp",        "max"),
        model_count    = ("model",       "count"),
        avg_hp         = ("engine_hp",   "mean"),
        avg_popularity = ("popularity",  "mean"),
        avg_highway_mpg= ("highway_mpg", "mean")
    )
    .reset_index()
    .sort_values("avg_msrp", ascending=False)
    .round(1)
)
brand_df.to_csv(f"{TAB_DIR}/task4_brand_avg_msrp.csv", index=False)
print(f"       Saved: task4_brand_avg_msrp.csv  ({len(brand_df)} brands)")

top25 = brand_df.head(25).sort_values("avg_msrp", ascending=True)

fig, ax = plt.subplots(figsize=(12, 10))
colors_bar = sns.color_palette("Blues_r", len(top25))
bars = ax.barh(top25["make"], top25["avg_msrp"],
               color=colors_bar, edgecolor="white", linewidth=0.4)
ax.set_title("Task 4 : Top 25 Car Brands by Average MSRP",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Average MSRP ($)")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
for bar, val in zip(bars, top25["avg_msrp"]):
    ax.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
            f"${val/1000:.1f}k", va="center", fontsize=8.5)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/seg_02_top_brands_msrp.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: seg_02_top_brands_msrp.png")


# ------------------------------------------------------------
# 3. BRAND x BODY STYLE HEATMAP - Dashboard Tasks 1 & 2
# ------------------------------------------------------------
print("\n[3/4] Building brand x body style MSRP heatmap...")
pivot = df.pivot_table(
    values="msrp",
    index="make",
    columns="vehicle_style",
    aggfunc="mean"
)
top25_makes = brand_df["make"].head(25).tolist()
pivot_top   = pivot.loc[pivot.index.isin(top25_makes)].fillna(0)
pivot_top_k = (pivot_top / 1000).round(1)
pivot_top_k = pivot_top_k.loc[top25_makes[::-1]]

fig, ax = plt.subplots(figsize=(18, 11))
sns.heatmap(
    pivot_top_k,
    cmap="YlOrRd",
    annot=True,
    fmt=".0f",
    linewidths=0.3,
    linecolor="white",
    annot_kws={"size": 7.5},
    cbar_kws={"label": "Avg MSRP ($000s)"},
    ax=ax
)
ax.set_title(
    "Dashboard Tasks 1 & 2 : Avg MSRP ($000s) - Brand vs Body Style\n"
    "(Top 25 brands | 0 = no model in that combination)",
    fontsize=12, fontweight="bold"
)
ax.set_xlabel("Vehicle Style")
ax.set_ylabel("Brand")
ax.tick_params(axis="x", rotation=40)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/seg_03_brand_style_heatmap.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: seg_03_brand_style_heatmap.png")


# ------------------------------------------------------------
# 4. POPULARITY vs PRICE SCATTER - coloured by price tier
# ------------------------------------------------------------
print("\n[4/4] Plotting popularity vs price by tier...")
tier_colors = {
    "Budget"      : "#74c476",
    "Mid-Range"   : "#41ab5d",
    "Premium"     : "#238b45",
    "Luxury"      : "#006d2c",
    "Ultra-Luxury": "#00441b"
}

fig, ax = plt.subplots(figsize=(11, 7))
for tier, group in df.groupby("price_tier"):
    ax.scatter(
        group["msrp"], group["popularity"],
        alpha=0.35, s=12,
        color=tier_colors.get(tier, "grey"),
        label=tier
    )
ax.set_title("Popularity Score vs MSRP - by Price Tier",
             fontsize=13, fontweight="bold")
ax.set_xlabel("MSRP ($)")
ax.set_ylabel("Popularity Score")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax.legend(title="Price Tier", loc="upper right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/seg_04_popularity_vs_price.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: seg_04_popularity_vs_price.png")


# -- Summary --------------------------------------------------
print("\n" + "=" * 60)
print("  MARKET SEGMENTATION COMPLETE")
print("=" * 60)
print(f"\n  Total brands analysed   : {len(brand_df)}")
print(f"  Total market categories : {len(cat_df)}")
print(f"\n  Highest avg MSRP brand  : {brand_df.iloc[0]['make']}  "
      f"(${brand_df.iloc[0]['avg_msrp']:,.0f})")
print(f"  Lowest  avg MSRP brand  : {brand_df.iloc[-1]['make']}  "
      f"(${brand_df.iloc[-1]['avg_msrp']:,.0f})")
print(f"\n  Most popular category   : {cat_df.iloc[0]['market_category']}  "
      f"(avg popularity: {cat_df.iloc[0]['avg_popularity']:.0f})")
print("\n  Next step -> python/05_correlation_analysis.py")
