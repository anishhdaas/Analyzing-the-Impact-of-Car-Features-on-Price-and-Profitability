"""
================================================================
FILE        : python/02_eda_visualization.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Exploratory Data Analysis - generate 10 charts
              covering distributions, trends, and relationships.
              Works alongside sql/03_eda_queries.sql.
RUN ORDER   : Step 5 - after python/01_data_cleaning.py
NEXT SCRIPT : python/03_regression_analysis.py
OUTPUTS     : outputs/figures/eda_01_msrp_distribution.png
              outputs/figures/eda_02_models_per_year.png
              outputs/figures/eda_03_avg_msrp_by_style.png
              outputs/figures/eda_04_fuel_type_combo.png
              outputs/figures/eda_05_msrp_by_transmission.png
              outputs/figures/eda_06_price_tier_distribution.png
              outputs/figures/eda_07_avg_msrp_over_time.png
              outputs/figures/eda_08_avg_msrp_by_drive_type.png
              outputs/figures/eda_09_mpg_over_time_by_size.png
              outputs/figures/eda_10_msrp_by_vehicle_size.png
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
os.makedirs(FIG_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

print("=" * 60)
print("  STEP 5 : Exploratory Data Analysis - Visualizations")
print("=" * 60)

# -- Load cleaned data ----------------------------------------
df = pd.read_csv(CLEAN_PATH)
print(f"\n  Loaded {len(df):,} rows from {CLEAN_PATH}\n")


# ------------------------------------------------------------
# CHART 1 : MSRP Distribution - Raw and Log Scale
# Insight  : MSRP is right-skewed; log scale shows near-normal
# ------------------------------------------------------------
print("[1/10] Plotting MSRP distribution...")
fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle("MSRP Distribution - Raw vs Log Scale", fontsize=14, fontweight="bold")

axes[0].hist(df["msrp"], bins=80, color="#2c7bb6", edgecolor="white", linewidth=0.4)
axes[0].set_title("Raw Scale")
axes[0].set_xlabel("MSRP ($)")
axes[0].set_ylabel("Count")
axes[0].xaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))

axes[1].hist(df["log_msrp"], bins=60, color="#d7191c", edgecolor="white", linewidth=0.4)
axes[1].set_title("Log Scale (Natural Log)")
axes[1].set_xlabel("log(MSRP)")
axes[1].set_ylabel("Count")

plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_01_msrp_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_01_msrp_distribution.png")


# ------------------------------------------------------------
# CHART 2 : Number of Car Models Released per Year
# Insight  : Dataset coverage and density across time
# ------------------------------------------------------------
print("[2/10] Plotting models per year...")
year_df = df.groupby("year").size().reset_index(name="count")

fig, ax = plt.subplots(figsize=(16, 5))
ax.bar(year_df["year"], year_df["count"],
       color="#4393c3", edgecolor="white", linewidth=0.4)
ax.set_title("Number of Car Models Released per Year",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Models")
ax.axhline(year_df["count"].mean(), color="red", linestyle="--",
           linewidth=1.2, label=f"Avg: {year_df['count'].mean():.0f}")
ax.legend()
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_02_models_per_year.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_02_models_per_year.png")


# ------------------------------------------------------------
# CHART 3 : Average MSRP by Vehicle Style (Horizontal Bar)
# Insight  : Convertibles and coupes command premium prices
# ------------------------------------------------------------
print("[3/10] Plotting avg MSRP by vehicle style...")
style_df = (df.groupby("vehicle_style")["msrp"]
              .mean()
              .sort_values(ascending=True)
              .reset_index())
style_df.columns = ["vehicle_style", "avg_msrp"]

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(
    style_df["vehicle_style"], style_df["avg_msrp"],
    color=sns.color_palette("Blues_r", len(style_df))
)
ax.set_title("Average MSRP by Vehicle Style", fontsize=14, fontweight="bold")
ax.set_xlabel("Average MSRP ($)")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
for bar, val in zip(bars, style_df["avg_msrp"]):
    ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
            f"${val/1000:.1f}k", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_03_avg_msrp_by_style.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_03_avg_msrp_by_style.png")


# ------------------------------------------------------------
# CHART 4 : Engine Fuel Type - Count and Avg MSRP (Combo)
# Insight  : Gasoline dominates; electric/hybrid are premium
# ------------------------------------------------------------
print("[4/10] Plotting fuel type distribution...")
fuel_df = (df.groupby("engine_fuel_type")
             .agg(count=("msrp", "count"), avg_msrp=("msrp", "mean"))
             .reset_index()
             .sort_values("count", ascending=False))

fig, ax1 = plt.subplots(figsize=(14, 6))
ax1.bar(fuel_df["engine_fuel_type"], fuel_df["count"],
        color="#4393c3", alpha=0.85, label="Model Count")
ax1.set_xlabel("Engine Fuel Type")
ax1.set_ylabel("Number of Models", color="#4393c3")
ax1.tick_params(axis="x", rotation=30)

ax2 = ax1.twinx()
ax2.plot(fuel_df["engine_fuel_type"], fuel_df["avg_msrp"],
         color="#d73027", marker="o", linewidth=2, label="Avg MSRP")
ax2.set_ylabel("Average MSRP ($)", color="#d73027")
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))

fig.suptitle("Engine Fuel Type - Model Count vs Average MSRP",
             fontsize=14, fontweight="bold")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_04_fuel_type_combo.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_04_fuel_type_combo.png")


# ------------------------------------------------------------
# CHART 5 : MSRP by Transmission Type (Box Plot)
# Insight  : AUTOMATED_MANUAL and DIRECT_DRIVE are premium
# ------------------------------------------------------------
print("[5/10] Plotting MSRP by transmission type...")
trans_order = (df.groupby("transmission_type")["msrp"]
                 .median()
                 .sort_values(ascending=False)
                 .index.tolist())

fig, ax = plt.subplots(figsize=(13, 6))
sns.boxplot(x="transmission_type", y="msrp", data=df,
            order=trans_order, palette="pastel", ax=ax)
ax.set_title("MSRP Distribution by Transmission Type",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Transmission Type")
ax.set_ylabel("MSRP ($) - Log Scale")
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_05_msrp_by_transmission.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_05_msrp_by_transmission.png")


# ------------------------------------------------------------
# CHART 6 : Price Tier Distribution - Pie Chart
# Insight  : Mid-Range and Budget make up the majority
# ------------------------------------------------------------
print("[6/10] Plotting price tier distribution...")
tier_order  = ["Budget", "Mid-Range", "Premium", "Luxury", "Ultra-Luxury"]
tier_counts = df["price_tier"].value_counts().reindex(tier_order).dropna()
tier_colors = ["#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"]

fig, ax = plt.subplots(figsize=(9, 9))
wedges, texts, autotexts = ax.pie(
    tier_counts,
    labels=tier_counts.index,
    autopct="%1.1f%%",
    colors=tier_colors,
    startangle=140,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5}
)
for t in autotexts:
    t.set_fontsize(11)
ax.set_title("Car Distribution by Price Tier", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_06_price_tier_distribution.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_06_price_tier_distribution.png")


# ------------------------------------------------------------
# CHART 7 : Average MSRP Over Time (Line + Area)
# Insight  : Prices trend upward - especially post-2000
# ------------------------------------------------------------
print("[7/10] Plotting avg MSRP over time...")
yr_df = df.groupby("year").agg(
    avg_msrp=("msrp", "mean"),
    count   =("msrp", "count")
).reset_index()

fig, ax = plt.subplots(figsize=(15, 5))
ax.plot(yr_df["year"], yr_df["avg_msrp"], color="#2171b5",
        marker="o", markersize=4, linewidth=2, zorder=3)
ax.fill_between(yr_df["year"], yr_df["avg_msrp"],
                alpha=0.15, color="#2171b5")
ax.set_title("Average MSRP Over Time", fontsize=14, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Average MSRP ($)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_07_avg_msrp_over_time.png", dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_07_avg_msrp_over_time.png")


# ------------------------------------------------------------
# CHART 8 : Average MSRP by Drive Type (Bar)
# Insight  : AWD and RWD vehicles are priced higher than FWD
# ------------------------------------------------------------
print("[8/10] Plotting avg MSRP by drive type...")
drive_df = (df.groupby("driven_wheels")["msrp"]
              .mean()
              .sort_values(ascending=False)
              .reset_index())
drive_df.columns = ["driven_wheels", "avg_msrp"]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(
    drive_df["driven_wheels"], drive_df["avg_msrp"],
    color=["#2c7bb6", "#abd9e9", "#fdae61", "#d7191c"],
    edgecolor="white", linewidth=0.5, width=0.5
)
ax.set_title("Average MSRP by Drive Type", fontsize=14, fontweight="bold")
ax.set_xlabel("Driven Wheels")
ax.set_ylabel("Average MSRP ($)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 400,
            f"${bar.get_height()/1000:.1f}k",
            ha="center", va="bottom", fontsize=10)
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_08_avg_msrp_by_drive_type.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_08_avg_msrp_by_drive_type.png")


# ------------------------------------------------------------
# CHART 9 : Avg Highway MPG Over Time by Vehicle Size
# Insight  : Compact cars consistently lead in fuel efficiency
# ------------------------------------------------------------
print("[9/10] Plotting MPG over time by vehicle size...")
mpg_size = (df.groupby(["year", "vehicle_size"])["highway_mpg"]
              .mean()
              .reset_index())
colors = {"Compact": "#1a9850", "Midsize": "#fdae61", "Large": "#d73027"}

fig, ax = plt.subplots(figsize=(15, 5))
for size in df["vehicle_size"].unique():
    subset = mpg_size[mpg_size["vehicle_size"] == size]
    ax.plot(subset["year"], subset["highway_mpg"],
            marker="o", markersize=3, linewidth=1.8,
            label=size, color=colors.get(size, "grey"))
ax.set_title("Average Highway MPG Over Time by Vehicle Size",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Highway MPG")
ax.legend(title="Vehicle Size")
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_09_mpg_over_time_by_size.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_09_mpg_over_time_by_size.png")


# ------------------------------------------------------------
# CHART 10 : MSRP Distribution by Vehicle Size (Box Plot)
# Insight  : Large vehicles have wider price variance
# ------------------------------------------------------------
print("[10/10] Plotting MSRP by vehicle size...")
size_order = (df.groupby("vehicle_size")["msrp"]
                .median()
                .sort_values(ascending=False)
                .index.tolist())

fig, ax = plt.subplots(figsize=(9, 6))
sns.boxplot(x="vehicle_size", y="msrp", data=df,
            order=size_order, palette="Set2", ax=ax)
ax.set_title("MSRP Distribution by Vehicle Size",
             fontsize=14, fontweight="bold")
ax.set_xlabel("Vehicle Size")
ax.set_ylabel("MSRP ($) - Log Scale")
ax.set_yscale("log")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
plt.tight_layout()
plt.savefig(f"{FIG_DIR}/eda_10_msrp_by_vehicle_size.png",
            dpi=150, bbox_inches="tight")
plt.close()
print("        Saved: eda_10_msrp_by_vehicle_size.png")


# -- Summary --------------------------------------------------
print("\n" + "=" * 60)
print("  EDA COMPLETE - 10 charts saved to outputs/figures/")
print("=" * 60)
charts = [
    ("eda_01", "MSRP Distribution - Raw vs Log"),
    ("eda_02", "Models Released per Year"),
    ("eda_03", "Avg MSRP by Vehicle Style"),
    ("eda_04", "Fuel Type - Count + Avg MSRP Combo"),
    ("eda_05", "MSRP by Transmission Type"),
    ("eda_06", "Price Tier Distribution (Pie)"),
    ("eda_07", "Avg MSRP Over Time"),
    ("eda_08", "Avg MSRP by Drive Type"),
    ("eda_09", "Highway MPG Over Time by Vehicle Size"),
    ("eda_10", "MSRP by Vehicle Size"),
]
for code, desc in charts:
    print(f"    {code}  ->  {desc}")
print("\n  Next step -> python/03_regression_analysis.py")
