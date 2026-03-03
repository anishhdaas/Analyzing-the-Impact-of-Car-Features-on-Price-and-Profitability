"""
================================================================
FILE        : python/01_data_cleaning.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Load raw Dataset.xlsx, perform thorough cleaning
              and preprocessing, export cleaned CSV, and load
              into SQLite database for SQL-based analysis.
RUN ORDER   : Step 4 - after sql/02_data_cleaning.sql
NEXT SCRIPT : python/02_eda_visualization.py
OUTPUTS     : data/cleaned/car_data_cleaned.csv
              car_data.db  (SQLite - table: car_features_clean)
================================================================
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import warnings

warnings.filterwarnings("ignore")

# -- Paths ----------------------------------------------------
RAW_PATH   = "data/raw/Dataset.xlsx"
CLEAN_PATH = "data/cleaned/car_data_cleaned.csv"
DB_PATH    = "car_data.db"

os.makedirs("data/cleaned",    exist_ok=True)
os.makedirs("outputs/figures", exist_ok=True)
os.makedirs("outputs/tables",  exist_ok=True)

print("=" * 60)
print("  STEP 4 : Python Data Cleaning & Preprocessing")
print("=" * 60)


# ------------------------------------------------------------
# 1. LOAD RAW DATA
# ------------------------------------------------------------
print("\n[1/12] Loading raw dataset from Excel...")
df = pd.read_excel(RAW_PATH)
print(f"       Raw shape : {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"       Columns   : {list(df.columns)}")


# ------------------------------------------------------------
# 2. STANDARDISE COLUMN NAMES
#    - strip whitespace, lowercase, replace spaces with _
#    - remove any character that is not a letter, digit, or _
# ------------------------------------------------------------
print("\n[2/12] Standardising column names...")
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)
print(f"       Cleaned columns: {list(df.columns)}")


# ------------------------------------------------------------
# 3. NULL AUDIT
#    - Report nulls per column before any imputation
# ------------------------------------------------------------
print("\n[3/12] Null audit (before cleaning):")
null_counts = df.isnull().sum()
null_pct    = (null_counts / len(df) * 100).round(2)
null_report = pd.DataFrame({
    "null_count": null_counts,
    "null_pct"  : null_pct
})
affected = null_report[null_report["null_count"] > 0]
if affected.empty:
    print("       No nulls found.")
else:
    print(affected.to_string())

print(f"\n       Total rows      : {len(df):,}")
print(f"       Duplicate rows  : "
      f"{df.duplicated(subset=['make','model','year','vehicle_style']).sum():,}")


# ------------------------------------------------------------
# 4. REMOVE DUPLICATES
#    - Keep first occurrence of each make+model+year+style
# ------------------------------------------------------------
print("\n[4/12] Removing duplicate rows...")
before = len(df)
df.drop_duplicates(
    subset=["make", "model", "year", "vehicle_style"],
    keep="first",
    inplace=True
)
print(f"       Removed  : {before - len(df):,} duplicate rows")
print(f"       Remaining: {len(df):,} rows")


# ------------------------------------------------------------
# 5. FILTER INVALID MSRP
#    - Drop rows where msrp is null, zero, or negative
# ------------------------------------------------------------
print("\n[5/12] Filtering invalid MSRP values...")
before = len(df)
df = df[(df["msrp"].notna()) & (df["msrp"] > 0)]
print(f"       Removed : {before - len(df):,} rows with null/zero/negative MSRP")


# ------------------------------------------------------------
# 6. IMPUTE MISSING NUMERICAL VALUES
#    engine_hp        -> median of non-null values
#    engine_cylinders -> mode (most frequent = 4)
#    number_of_doors  -> 4 (universal standard default)
# ------------------------------------------------------------
print("\n[6/12] Imputing missing numerical values...")

hp_median = df["engine_hp"].median()
hp_nulls  = df["engine_hp"].isnull().sum()
df["engine_hp"].fillna(hp_median, inplace=True)
print(f"       engine_hp        : {hp_nulls} nulls -> filled with median ({hp_median:.1f} HP)")

cyl_mode  = int(df["engine_cylinders"].mode()[0])
cyl_nulls = df["engine_cylinders"].isnull().sum()
df["engine_cylinders"].fillna(cyl_mode, inplace=True)
df["engine_cylinders"] = df["engine_cylinders"].astype(int)
print(f"       engine_cylinders : {cyl_nulls} nulls -> filled with mode ({cyl_mode})")

door_nulls = df["number_of_doors"].isnull().sum()
df["number_of_doors"].fillna(4, inplace=True)
df["number_of_doors"] = df["number_of_doors"].astype(int)
print(f"       number_of_doors  : {door_nulls} nulls -> filled with 4")


# ------------------------------------------------------------
# 7. IMPUTE MISSING CATEGORICAL VALUES
#    engine_fuel_type  -> 'unknown'   (lowercase + strip)
#    market_category   -> 'Unclassified'
#    transmission_type -> 'AUTOMATIC' (uppercase + strip)
# ------------------------------------------------------------
print("\n[7/12] Imputing missing categorical values...")

fuel_nulls = df["engine_fuel_type"].isnull().sum()
df["engine_fuel_type"] = (
    df["engine_fuel_type"]
    .fillna("unknown")
    .str.lower()
    .str.strip()
)
print(f"       engine_fuel_type  : {fuel_nulls} nulls -> 'unknown' (lowercased + stripped)")

cat_nulls = df["market_category"].isnull().sum()
df["market_category"].fillna("Unclassified", inplace=True)
print(f"       market_category   : {cat_nulls} nulls -> 'Unclassified'")

trans_nulls = df["transmission_type"].isnull().sum()
df["transmission_type"] = (
    df["transmission_type"]
    .fillna("AUTOMATIC")
    .str.upper()
    .str.strip()
)
print(f"       transmission_type : {trans_nulls} nulls -> 'AUTOMATIC' (uppercased + stripped)")


# ------------------------------------------------------------
# 8. REMOVE EXTREME OUTLIERS
#    msrp      -> cap at $2,000,000 (removes data-entry errors)
#    engine_hp -> cap at 2,000 HP   (removes data-entry errors)
#    Note: legitimate ultra-luxury cars (Bugatti, Rolls) are kept
# ------------------------------------------------------------
print("\n[8/12] Removing extreme outliers...")
before = len(df)
df = df[(df["msrp"] <= 2_000_000) & (df["engine_hp"] <= 2_000)]
print(f"       Removed  : {before - len(df):,} extreme outlier rows")
print(f"       Remaining: {len(df):,} rows")


# ------------------------------------------------------------
# 9. TRIM REMAINING TEXT COLUMNS
# ------------------------------------------------------------
print("\n[9/12] Trimming whitespace from text columns...")
text_cols = [
    "make", "model", "driven_wheels",
    "vehicle_size", "vehicle_style", "market_category"
]
for col in text_cols:
    df[col] = df[col].astype(str).str.strip()
print(f"       Trimmed: {text_cols}")


# ------------------------------------------------------------
# 10. CREATE DERIVED COLUMNS
#     mpg_avg       -> average of highway and city MPG
#     log_msrp      -> natural log of MSRP (regression normality)
#     hp_per_dollar -> engine_hp / msrp (value-for-money metric)
#     price_tier    -> 5-bracket segment from MSRP
# ------------------------------------------------------------
print("\n[10/12] Creating derived columns...")

df["mpg_avg"] = ((df["highway_mpg"] + df["city_mpg"]) / 2).round(1)
print("        mpg_avg       -> (highway_mpg + city_mpg) / 2")

df["log_msrp"] = np.log(df["msrp"]).round(4)
print("        log_msrp      -> natural log of msrp")

df["hp_per_dollar"] = (df["engine_hp"] / df["msrp"]).round(6)
print("        hp_per_dollar -> engine_hp / msrp")

def assign_price_tier(msrp):
    if msrp < 20_000:
        return "Budget"
    elif msrp < 40_000:
        return "Mid-Range"
    elif msrp < 70_000:
        return "Premium"
    elif msrp < 150_000:
        return "Luxury"
    else:
        return "Ultra-Luxury"

df["price_tier"] = df["msrp"].apply(assign_price_tier)
tier_counts = df["price_tier"].value_counts().to_dict()
print(f"        price_tier    -> 5 tiers: {tier_counts}")


# ------------------------------------------------------------
# 11. FINAL TYPE CASTING AND RESET INDEX
# ------------------------------------------------------------
print("\n[11/12] Finalising data types...")
df["year"]       = df["year"].astype(int)
df["msrp"]       = df["msrp"].astype(int)
df["popularity"] = df["popularity"].fillna(0).astype(int)
df["engine_hp"]  = df["engine_hp"].round(1)

df.reset_index(drop=True, inplace=True)
print(f"        Final shape  : {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"        Columns      : {list(df.columns)}")


# ------------------------------------------------------------
# 12. EXPORT - CSV + SQLite
# ------------------------------------------------------------
print(f"\n[12/12] Exporting cleaned data...")

# Export CSV
df.to_csv(CLEAN_PATH, index=False)
print(f"        CSV saved   -> {CLEAN_PATH}")

# Load into SQLite
conn = sqlite3.connect(DB_PATH)
df.to_sql("car_features_clean", conn, if_exists="replace", index=False)
conn.commit()
row_count = pd.read_sql(
    "SELECT COUNT(*) AS n FROM car_features_clean", conn
).iloc[0, 0]
print(f"        SQLite DB   -> {DB_PATH}  ({row_count:,} rows in car_features_clean)")
conn.close()


# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------
print("\n" + "=" * 60)
print("  CLEANING COMPLETE - Summary Statistics")
print("=" * 60)
summary_cols = [
    "engine_hp", "engine_cylinders",
    "highway_mpg", "city_mpg", "msrp", "popularity"
]
print(df[summary_cols].describe().round(2).to_string())

print("\n  Price Tier Distribution:")
print(df["price_tier"].value_counts().to_string())

print("\n  Null check after cleaning:")
remaining_nulls = df.isnull().sum()
if remaining_nulls.sum() > 0:
    print(remaining_nulls[remaining_nulls > 0].to_string())
else:
    print("  No nulls remaining.")

print("\n  Next step -> python/02_eda_visualization.py")
