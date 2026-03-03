-- =============================================================
-- FILE: sql/01_create_schema.sql
-- PURPOSE: Create the database schema for the Car Features
--          and MSRP analysis project.
-- DATABASE: SQLite (compatible with PostgreSQL with minor tweaks)
-- RUN: First script in the pipeline — run before all others.
-- NOTE: Indexes are intentionally NOT created here.
--       They are created at the end of 02_data_cleaning.sql
--       after data is loaded, which is faster and avoids
--       empty-table errors in certain SQL clients.
-- =============================================================


-- -------------------------------------------------------------
-- SAFETY: Drop tables if they exist (for clean re-runs)
-- Drop clean table first due to logical dependency order
-- -------------------------------------------------------------
DROP TABLE IF EXISTS car_features_clean;
DROP TABLE IF EXISTS car_features_raw;


-- -------------------------------------------------------------
-- TABLE 1: car_features_raw
-- Stores data exactly as imported from Dataset.xlsx (CSV export)
-- All columns are nullable to accept raw/dirty data as-is
-- -------------------------------------------------------------
CREATE TABLE car_features_raw (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    make              TEXT,
    model             TEXT,
    year              INTEGER,
    engine_fuel_type  TEXT,
    engine_hp         REAL,
    engine_cylinders  REAL,
    transmission_type TEXT,
    driven_wheels     TEXT,
    number_of_doors   REAL,
    market_category   TEXT,
    vehicle_size      TEXT,
    vehicle_style     TEXT,
    highway_mpg       INTEGER,
    city_mpg          INTEGER,
    popularity        INTEGER,
    msrp              INTEGER
);


-- -------------------------------------------------------------
-- TABLE 2: car_features_clean
-- Stores cleaned, validated, and enriched data.
-- Populated by sql/02_data_cleaning.sql
-- -------------------------------------------------------------
CREATE TABLE car_features_clean (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    make              TEXT     NOT NULL,
    model             TEXT     NOT NULL,
    year              INTEGER  NOT NULL,
    engine_fuel_type  TEXT     NOT NULL DEFAULT 'unknown',
    engine_hp         REAL     NOT NULL,
    engine_cylinders  INTEGER  NOT NULL,
    transmission_type TEXT     NOT NULL,
    driven_wheels     TEXT     NOT NULL,
    number_of_doors   INTEGER  NOT NULL DEFAULT 4,
    market_category   TEXT,
    vehicle_size      TEXT     NOT NULL,
    vehicle_style     TEXT     NOT NULL,
    highway_mpg       INTEGER  NOT NULL,
    city_mpg          INTEGER  NOT NULL,
    popularity        INTEGER  NOT NULL DEFAULT 0,
    msrp              INTEGER  NOT NULL,
    price_tier        TEXT,
    mpg_avg           REAL
);


-- -------------------------------------------------------------
-- LOAD INSTRUCTIONS
-- Export Dataset.xlsx to CSV first, then load using one of:
--
-- Option A — SQLite CLI:
--   sqlite3 car_data.db
--   .mode csv
--   .headers on
--   .import data/raw/car_data_raw.csv car_features_raw
--
-- Option B — Python (recommended, handles encoding safely):
--   Run python/01_data_cleaning.py
--   It loads the Excel file directly and writes to both
--   the CSV and the SQLite DB automatically.
-- -------------------------------------------------------------


-- -------------------------------------------------------------
-- VERIFY: Confirm both tables were created successfully
-- -------------------------------------------------------------
SELECT
    name        AS table_name,
    type        AS object_type
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
