# 🚗 Analyzing the Impact of Car Features on Price and Profitability

> **End-to-End Data Analytics Project** | SQL · Python · Excel · Data Visualization

---

## 📌 Table of Contents

1. [Project Overview](#project-overview)
2. [Business Problem](#business-problem)
3. [Dataset Description](#dataset-description)
4. [Repository Structure](#repository-structure)
5. [Tech Stack](#tech-stack)
6. [Project Workflow](#project-workflow)
7. [Key Insights](#key-insights)
8. [How to Run](#how-to-run)
9. [Results & Dashboard](#results--dashboard)
10. [Future Scope](#future-scope)

---

## Project Overview

The automotive industry is undergoing rapid transformation — driven by electrification, sustainability mandates, and shifting consumer preferences. This project investigates how a car manufacturer can **optimize pricing and product development decisions** to maximize profitability while aligning with consumer demand.

Using a real-world dataset of **11,159 car models**, we perform:
- **SQL-based data exploration & cleaning**
- **Python-based statistical analysis & regression modeling**
- **Excel interactive dashboard** for business stakeholders

---

## Business Problem

> *"How can a car manufacturer optimize pricing and product development decisions to maximize profitability while meeting consumer demand?"*

To address this, we explore:
- Which car **features** (engine power, fuel type, cylinders, transmission) most strongly predict **MSRP**?
- Which **market categories** and **brands** generate the highest average prices?
- How does **fuel efficiency** relate to engine configuration?
- What **consumer popularity** signals exist across body styles and categories?

---

## Dataset Description

| Attribute | Detail |
|---|---|
| **Source** | Kaggle – "Car Features and MSRP" by Cooper Union |
| **Observations** | 11,159 car models |
| **Variables** | 16 |
| **Last Updated** | 2017 |

### Variables

| Column | Description |
|---|---|
| `Make` | Car brand (BMW, Toyota, etc.) |
| `Model` | Specific car model |
| `Year` | Year of release |
| `Engine Fuel Type` | Fuel type (gasoline, diesel, electric, etc.) |
| `Engine HP` | Engine horsepower |
| `Engine Cylinders` | Number of cylinders |
| `Transmission Type` | Automatic / Manual / CVT |
| `Driven_Wheels` | Front / Rear / All-wheel drive |
| `Number of Doors` | Door count |
| `Market Category` | Luxury, Performance, Crossover, etc. |
| `Vehicle Size` | Compact / Midsize / Large |
| `Vehicle Style` | Sedan, Coupe, SUV, etc. |
| `highway MPG` | Highway miles per gallon |
| `city mpg` | City miles per gallon |
| `Popularity` | Views on Edmunds.com |
| `MSRP` | Manufacturer's Suggested Retail Price ($) |

---

## Repository Structure

```
car-features-price-profitability/
│
├── README.md                          ← You are here
│
├── data/
│   ├── raw/
│   │   └── Dataset.xlsx               ← Original raw dataset
│   └── cleaned/
│       └── car_data_cleaned.csv       ← Output of cleaning step
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_data_cleaning.sql
│   ├── 03_eda_queries.sql
│   └── 04_business_insights.sql
│
├── python/
│   ├── 01_data_cleaning.py
│   ├── 02_eda_visualization.py
│   ├── 03_regression_analysis.py
│   ├── 04_market_segmentation.py
│   ├── 05_correlation_analysis.py
│   └── 06_dashboard_data_prep.py
│
├── excel/
│   └── Car_Analysis_Dashboard.xlsx
│
├── reports/
│   └── Car_Features_Profitability_Report.pdf
│
├── outputs/
│   └── figures/                       ← All generated plots saved here
│
└── requirements.txt
```

---

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| Data Storage & Querying | SQLite / PostgreSQL + SQL | Schema creation, cleaning, EDA |
| Data Analysis | Python (pandas, numpy, scipy) | Cleaning, statistics, regression |
| Visualization | matplotlib, seaborn, plotly | Charts, heatmaps, scatter plots |
| ML / Modeling | scikit-learn | Linear regression, feature importance |
| Dashboard | Microsoft Excel | Interactive slicers, pivot charts |
| Reporting | PDF / PowerPoint | Stakeholder presentation |
| Version Control | Git + GitHub | Code repository |

---

## Project Workflow

```
Step 1:  Raw Data Ingestion          → data/raw/Dataset.xlsx
Step 2:  SQL Schema + Data Loading   → sql/01_create_schema.sql
Step 3:  SQL Data Cleaning           → sql/02_data_cleaning.sql
Step 4:  Python Cleaning             → python/01_data_cleaning.py
Step 5:  EDA (SQL + Python)          → sql/03_eda_queries.sql + python/02_eda_visualization.py
Step 6:  Business Insights (SQL)     → sql/04_business_insights.sql
Step 7:  Regression Analysis         → python/03_regression_analysis.py
Step 8:  Market Segmentation         → python/04_market_segmentation.py
Step 9:  Correlation Analysis        → python/05_correlation_analysis.py
Step 10: Dashboard Prep              → python/06_dashboard_data_prep.py → Excel
Step 11: Final Report                → reports/Car_Features_Profitability_Report.pdf
```

---

## Key Insights

1. **Engine HP is the strongest predictor of MSRP** — ~$150 price increase per additional HP.
2. **Luxury and Performance categories** command 3–5x higher average MSRPs than Economy segments.
3. **Exotic brands** (Bugatti, Maybach, Lamborghini) lead average MSRP rankings by a wide margin.
4. **Cylinders negatively correlate with fuel efficiency** — correlation coefficient ≈ -0.75.
5. **Automatic transmissions** are associated with significantly higher MSRPs than Manual.
6. **SUV and Convertible styles** are priced substantially higher than Sedans and Hatchbacks.
7. **Popularity scores** are not strongly correlated with price — affordable mass-market cars dominate view counts.

---

## How to Run

### Prerequisites

```bash
git clone https://github.com/yourusername/car-features-price-profitability.git
cd car-features-price-profitability
pip install -r requirements.txt
```

### Run Python Pipeline (in order)

```bash
python python/01_data_cleaning.py
python python/02_eda_visualization.py
python python/03_regression_analysis.py
python python/04_market_segmentation.py
python python/05_correlation_analysis.py
python python/06_dashboard_data_prep.py
```

### Run SQL Scripts

```bash
sqlite3 car_data.db < sql/01_create_schema.sql
sqlite3 car_data.db < sql/02_data_cleaning.sql
sqlite3 car_data.db < sql/03_eda_queries.sql
sqlite3 car_data.db < sql/04_business_insights.sql
```

---

## Results & Dashboard

The Excel dashboard contains **5 interactive sheets**:

| Sheet | Chart Type | Insight |
|---|---|---|
| Price by Brand & Style | Stacked Column | MSRP distribution across brands |
| Avg MSRP by Brand | Clustered Column | Highest/lowest MSRP brands |
| Transmission vs MSRP | Scatter Plot | Transmission impact on price |
| Fuel Efficiency Over Time | Line Chart | MPG trends by body style & year |
| HP vs MPG vs Price | Bubble Chart | Multi-variable brand comparison |

---

## Future Scope

- Incorporate **2020–2024 data** for EV/Hybrid pricing trends
- Build a **ML price prediction web app** using Streamlit
- Add **NLP sentiment analysis** on car reviews for popularity prediction
- Extend to **competitive benchmarking** across manufacturers

---
