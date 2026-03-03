"""
================================================================
FILE        : python/06_dashboard_data_prep.py
PROJECT     : Analyzing the Impact of Car Features on Price
              and Profitability
PURPOSE     : Generate all 5 aggregated data tables required
              for the interactive Excel dashboard, export each
              as individual CSV files, and consolidate them
              into a single multi-sheet Excel workbook ready
              for chart building and slicer setup.
RUN ORDER   : Step 10 - after python/05_correlation_analysis.py
NEXT STEP   : Open excel/Car_Analysis_Dashboard.xlsx and build
              charts from the pre-aggregated sheets.
OUTPUTS     : outputs/tables/dash_task1_msrp_brand_style.csv
              outputs/tables/dash_task2_avg_msrp_by_brand.csv
              outputs/tables/dash_task2_brand_style_detail.csv
              outputs/tables/dash_task3_transmission_msrp.csv
              outputs/tables/dash_task4_mpg_trend.csv
              outputs/tables/dash_task4_mpg_yoy_overall.csv
              outputs/tables/dash_task5_bubble_brand.csv
              excel/Car_Analysis_Dashboard.xlsx
================================================================
"""

import pandas as pd
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore")

# -- Config ---------------------------------------------------
CLEAN_PATH = "data/cleaned/car_data_cleaned.csv"
TAB_DIR    = "outputs/tables"
EXCEL_DIR  = "excel"
EXCEL_OUT  = f"{EXCEL_DIR}/Car_Analysis_Dashboard.xlsx"

os.makedirs(TAB_DIR,   exist_ok=True)
os.makedirs(EXCEL_DIR, exist_ok=True)

print("=" * 60)
print("  STEP 10 : Dashboard Data Preparation")
print("=" * 60)

df = pd.read_csv(CLEAN_PATH)
print(f"\n  Loaded {len(df):,} rows from {CLEAN_PATH}")
print(f"  Brands  : {df['make'].nunique()}")
print(f"  Styles  : {df['vehicle_style'].nunique()}")
print(f"  Years   : {df['year'].min()} - {df['year'].max()}\n")


# ------------------------------------------------------------
# DASHBOARD TASK 1
# Question : How does the distribution of car prices vary
#            by brand and body style?
# Chart    : Stacked column chart
# ------------------------------------------------------------
print("[1/5] Dashboard Task 1 - MSRP distribution by brand & style...")
task1 = (
    df.groupby(["make", "vehicle_style"])
    .agg(
        model_count = ("msrp", "count"),
        total_msrp  = ("msrp", "sum"),
        avg_msrp    = ("msrp", "mean"),
        min_msrp    = ("msrp", "min"),
        max_msrp    = ("msrp", "max")
    )
    .reset_index()
    .sort_values(["make", "avg_msrp"], ascending=[True, False])
)
task1[["total_msrp","avg_msrp","min_msrp","max_msrp"]] = \
    task1[["total_msrp","avg_msrp","min_msrp","max_msrp"]].round(0).astype(int)

task1.to_csv(f"{TAB_DIR}/dash_task1_msrp_brand_style.csv", index=False)
print(f"       Rows: {len(task1):,}  |  "
      f"Brands: {task1['make'].nunique()}  |  "
      f"Styles: {task1['vehicle_style'].nunique()}")
print(f"       Saved: dash_task1_msrp_brand_style.csv")


# ------------------------------------------------------------
# DASHBOARD TASK 2
# Question : Which car brands have the highest and lowest
#            average MSRPs by body style?
# Chart    : Clustered column chart
# ------------------------------------------------------------
print("\n[2/5] Dashboard Task 2 - Avg MSRP by brand...")
task2 = (
    df.groupby("make")
    .agg(
        avg_msrp        = ("msrp",        "mean"),
        min_msrp        = ("msrp",        "min"),
        max_msrp        = ("msrp",        "max"),
        model_count     = ("model",       "count"),
        avg_hp          = ("engine_hp",   "mean"),
        avg_highway_mpg = ("highway_mpg", "mean"),
        avg_popularity  = ("popularity",  "mean")
    )
    .reset_index()
    .sort_values("avg_msrp", ascending=False)
    .round({"avg_msrp": 0, "min_msrp": 0, "max_msrp": 0,
            "avg_hp": 1, "avg_highway_mpg": 2, "avg_popularity": 0})
)
task2_by_style = (
    df.groupby(["make", "vehicle_style"])
    .agg(avg_msrp=("msrp", "mean"), model_count=("msrp", "count"))
    .reset_index()
    .round({"avg_msrp": 0})
)
task2.to_csv(f"{TAB_DIR}/dash_task2_avg_msrp_by_brand.csv", index=False)
task2_by_style.to_csv(f"{TAB_DIR}/dash_task2_brand_style_detail.csv", index=False)
print(f"       Brands: {len(task2)}  |  "
      f"Highest: {task2.iloc[0]['make']} (${task2.iloc[0]['avg_msrp']:,.0f})  |  "
      f"Lowest: {task2.iloc[-1]['make']} (${task2.iloc[-1]['avg_msrp']:,.0f})")
print(f"       Saved: dash_task2_avg_msrp_by_brand.csv + dash_task2_brand_style_detail.csv")


# ------------------------------------------------------------
# DASHBOARD TASK 3
# Question : How does transmission type affect MSRP by style?
# Chart    : Scatter plot
# ------------------------------------------------------------
print("\n[3/5] Dashboard Task 3 - Transmission type vs MSRP by style...")
task3 = (
    df.groupby(["transmission_type", "vehicle_style"])
    .agg(
        model_count = ("msrp", "count"),
        avg_msrp    = ("msrp", "mean"),
        min_msrp    = ("msrp", "min"),
        max_msrp    = ("msrp", "max"),
        avg_hp      = ("engine_hp", "mean")
    )
    .reset_index()
    .sort_values(["transmission_type", "avg_msrp"], ascending=[True, False])
    .round({"avg_msrp": 0, "min_msrp": 0, "max_msrp": 0, "avg_hp": 1})
)
task3.to_csv(f"{TAB_DIR}/dash_task3_transmission_msrp.csv", index=False)
print(f"       Rows: {len(task3):,}  |  "
      f"Transmission types: {task3['transmission_type'].nunique()}  |  "
      f"Styles: {task3['vehicle_style'].nunique()}")
print(f"       Saved: dash_task3_transmission_msrp.csv")


# ------------------------------------------------------------
# DASHBOARD TASK 4
# Question : How does fuel efficiency vary by body style + year?
# Chart    : Line chart
# ------------------------------------------------------------
print("\n[4/5] Dashboard Task 4 - Fuel efficiency trend by year & style...")
task4 = (
    df.groupby(["year", "vehicle_style"])
    .agg(
        avg_highway_mpg  = ("highway_mpg", "mean"),
        avg_city_mpg     = ("city_mpg",    "mean"),
        avg_combined_mpg = ("mpg_avg",     "mean"),
        model_count      = ("msrp",        "count")
    )
    .reset_index()
    .sort_values(["year", "vehicle_style"])
    .round({"avg_highway_mpg": 2, "avg_city_mpg": 2, "avg_combined_mpg": 2})
)
task4_yoy = (
    df.groupby("year")
    .agg(
        avg_highway_mpg  = ("highway_mpg", "mean"),
        avg_city_mpg     = ("city_mpg",    "mean"),
        avg_combined_mpg = ("mpg_avg",     "mean"),
        total_models     = ("msrp",        "count")
    )
    .reset_index()
    .round(2)
)
task4.to_csv(f"{TAB_DIR}/dash_task4_mpg_trend.csv", index=False)
task4_yoy.to_csv(f"{TAB_DIR}/dash_task4_mpg_yoy_overall.csv", index=False)
print(f"       Rows: {len(task4):,}  |  "
      f"Years: {task4['year'].nunique()}  |  "
      f"Styles: {task4['vehicle_style'].nunique()}")
print(f"       Saved: dash_task4_mpg_trend.csv + dash_task4_mpg_yoy_overall.csv")


# ------------------------------------------------------------
# DASHBOARD TASK 5
# Question : HP, MPG, and Price by brand (bubble chart)
# Filter   : Brands with 5+ models
# ------------------------------------------------------------
print("\n[5/5] Dashboard Task 5 - HP, MPG & Price by brand...")
brand_counts     = df["make"].value_counts()
qualified_brands = brand_counts[brand_counts >= 5].index
task5 = (
    df[df["make"].isin(qualified_brands)]
    .groupby("make")
    .agg(
        avg_hp          = ("engine_hp",   "mean"),
        avg_highway_mpg = ("highway_mpg", "mean"),
        avg_city_mpg    = ("city_mpg",    "mean"),
        avg_msrp        = ("msrp",        "mean"),
        avg_popularity  = ("popularity",  "mean"),
        model_count     = ("model",       "count")
    )
    .reset_index()
    .sort_values("avg_msrp", ascending=False)
    .round({
        "avg_hp": 1, "avg_highway_mpg": 2,
        "avg_city_mpg": 2, "avg_msrp": 0, "avg_popularity": 0
    })
)
msrp_min = task5["avg_msrp"].min()
msrp_max = task5["avg_msrp"].max()
task5["bubble_size"] = (
    ((task5["avg_msrp"] - msrp_min) / (msrp_max - msrp_min)) * 99 + 1
).round(1)
task5.to_csv(f"{TAB_DIR}/dash_task5_bubble_brand.csv", index=False)
print(f"       Brands included: {len(task5)} (with 5+ models)")
print(f"       Saved: dash_task5_bubble_brand.csv")


# ------------------------------------------------------------
# CONSOLIDATE - Multi-sheet Excel Workbook
# ------------------------------------------------------------
print("\n  Consolidating all tables into Excel workbook...")

with pd.ExcelWriter(EXCEL_OUT, engine="xlsxwriter") as writer:
    wb = writer.book

    header_fmt = wb.add_format({
        "bold": True, "bg_color": "#2C5F8A", "font_color": "white",
        "border": 1, "align": "center", "valign": "vcenter"
    })

    def write_sheet(df_to_write, sheet_name, col_widths=None):
        df_to_write.to_excel(writer, sheet_name=sheet_name, index=False)
        ws = writer.sheets[sheet_name]
        for col_num, col_name in enumerate(df_to_write.columns):
            ws.write(0, col_num, col_name, header_fmt)
            width = col_widths.get(col_name, 15) if col_widths else 15
            ws.set_column(col_num, col_num, width)

    write_sheet(task1, "Task1_Price_Brand_Style",
                {"make": 18, "vehicle_style": 18,
                 "model_count": 13, "total_msrp": 14,
                 "avg_msrp": 13, "min_msrp": 12, "max_msrp": 12})

    write_sheet(task2, "Task2_AvgMSRP_Brand",
                {"make": 18, "avg_msrp": 13, "min_msrp": 12,
                 "max_msrp": 12, "model_count": 13,
                 "avg_hp": 10, "avg_highway_mpg": 16, "avg_popularity": 14})

    write_sheet(task3, "Task3_Transmission_MSRP",
                {"transmission_type": 20, "vehicle_style": 18,
                 "model_count": 13, "avg_msrp": 13,
                 "min_msrp": 12, "max_msrp": 12, "avg_hp": 10})

    write_sheet(task4, "Task4_MPG_Trend",
                {"year": 8, "vehicle_style": 18,
                 "avg_highway_mpg": 17, "avg_city_mpg": 14,
                 "avg_combined_mpg": 17, "model_count": 13})

    write_sheet(task5, "Task5_Bubble_Brand",
                {"make": 18, "avg_hp": 10, "avg_highway_mpg": 17,
                 "avg_city_mpg": 14, "avg_msrp": 13,
                 "avg_popularity": 14, "model_count": 13, "bubble_size": 12})

    write_sheet(df, "Full_Clean_Data")

    # README sheet
    ws_info  = wb.add_worksheet("README")
    ws_info.set_column(0, 0, 30)
    ws_info.set_column(1, 1, 70)
    title_fmt = wb.add_format({
        "bold": True, "font_size": 14,
        "bg_color": "#1F3864", "font_color": "white"
    })
    info_fmt = wb.add_format({"text_wrap": True, "valign": "top"})
    head_fmt = wb.add_format({"bold": True, "bg_color": "#D6E4F0"})

    ws_info.write(0, 0, "Car Features & Price Analysis", title_fmt)
    ws_info.write(0, 1, "Interactive Excel Dashboard",   title_fmt)
    ws_info.set_row(0, 25)

    readme_rows = [
        ("", ""),
        ("Sheet", "Purpose"),
        ("Task1_Price_Brand_Style",   "Stacked column chart: MSRP by brand and body style"),
        ("Task2_AvgMSRP_Brand",       "Clustered column chart: highest and lowest avg MSRP brands"),
        ("Task3_Transmission_MSRP",   "Scatter plot: transmission effect on MSRP by body style"),
        ("Task4_MPG_Trend",           "Line chart: fuel efficiency trend over years by body style"),
        ("Task5_Bubble_Brand",        "Bubble chart: HP (x) vs MPG (y) vs Price (bubble size)"),
        ("Full_Clean_Data",           "Complete cleaned dataset - source for all pivot tables"),
        ("", ""),
        ("Dashboard Tips", ""),
        ("Slicers",       "Add slicers on: make, vehicle_style, year, transmission_type, price_tier"),
        ("Bubble size",   "Use bubble_size column (1-100 normalised) for bubble chart sizing"),
        ("Chart colours", "Assign distinct colours per brand/style for visual differentiation"),
    ]
    for i, (label, desc) in enumerate(readme_rows, start=2):
        fmt = head_fmt if label in ("Sheet", "Dashboard Tips") else info_fmt
        ws_info.write(i, 0, label, fmt)
        ws_info.write(i, 1, desc,  fmt)

print(f"\n  Excel workbook saved -> {EXCEL_OUT}")
print(f"  Sheets: Task1 | Task2 | Task3 | Task4 | Task5 | Full_Clean_Data | README")


# -- Final Summary --------------------------------------------
print("\n" + "=" * 60)
print("  DASHBOARD PREP COMPLETE")
print("=" * 60)
tables = [
    ("dash_task1_msrp_brand_style.csv",  len(task1)),
    ("dash_task2_avg_msrp_by_brand.csv", len(task2)),
    ("dash_task3_transmission_msrp.csv", len(task3)),
    ("dash_task4_mpg_trend.csv",         len(task4)),
    ("dash_task5_bubble_brand.csv",      len(task5)),
]
print(f"\n  CSV files exported to {TAB_DIR}/:")
for name, rows in tables:
    print(f"    {name:45s}  {rows:>4} rows")

print(f"\n  Excel workbook   -> {EXCEL_OUT}")
print(f"  Total sheets     : 7")
print("\n" + "=" * 60)
print("  FULL PIPELINE COMPLETE")
print("=" * 60)
print("""
  Step 1  Raw data          -> data/raw/Dataset.xlsx
  Step 2  SQL Schema        -> sql/01_create_schema.sql
  Step 3  SQL Cleaning      -> sql/02_data_cleaning.sql
  Step 4  Python Cleaning   -> python/01_data_cleaning.py       done
  Step 5  EDA               -> python/02_eda_visualization.py   done
  Step 7  Regression        -> python/03_regression_analysis.py done
  Step 8  Segmentation      -> python/04_market_segmentation.py done
  Step 9  Correlation       -> python/05_correlation_analysis.py done
  Step 10 Dashboard Prep    -> python/06_dashboard_data_prep.py  done
  Step 11 Final Report      -> reports/ (PDF)
""")
