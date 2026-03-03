-- =============================================================
-- FILE: sql/02_data_cleaning.sql
-- PURPOSE: Audit raw data, clean and populate car_features_clean,
--          then create indexes after data is loaded.
-- RUN ORDER: Step 2 of 4 - after 01_create_schema.sql
-- =============================================================


-- -------------------------------------------------------------
-- STEP 1: Audit raw data - count nulls per column
-- -------------------------------------------------------------
SELECT
    COUNT(*)                                                    AS total_rows,
    SUM(CASE WHEN make              IS NULL THEN 1 ELSE 0 END) AS null_make,
    SUM(CASE WHEN model             IS NULL THEN 1 ELSE 0 END) AS null_model,
    SUM(CASE WHEN year              IS NULL THEN 1 ELSE 0 END) AS null_year,
    SUM(CASE WHEN engine_fuel_type  IS NULL THEN 1 ELSE 0 END) AS null_fuel_type,
    SUM(CASE WHEN engine_hp         IS NULL THEN 1 ELSE 0 END) AS null_engine_hp,
    SUM(CASE WHEN engine_cylinders  IS NULL THEN 1 ELSE 0 END) AS null_cylinders,
    SUM(CASE WHEN transmission_type IS NULL THEN 1 ELSE 0 END) AS null_transmission,
    SUM(CASE WHEN number_of_doors   IS NULL THEN 1 ELSE 0 END) AS null_doors,
    SUM(CASE WHEN market_category   IS NULL THEN 1 ELSE 0 END) AS null_market_cat,
    SUM(CASE WHEN highway_mpg       IS NULL THEN 1 ELSE 0 END) AS null_highway_mpg,
    SUM(CASE WHEN city_mpg          IS NULL THEN 1 ELSE 0 END) AS null_city_mpg,
    SUM(CASE WHEN msrp              IS NULL THEN 1 ELSE 0 END) AS null_msrp,
    SUM(CASE WHEN msrp <= 0         THEN 1 ELSE 0 END)         AS zero_or_neg_msrp
FROM car_features_raw;


-- -------------------------------------------------------------
-- STEP 2: Check for duplicate rows
-- Duplicate defined as same make + model + year + vehicle_style
-- -------------------------------------------------------------
SELECT
    make,
    model,
    year,
    vehicle_style,
    COUNT(*) AS duplicate_count
FROM car_features_raw
GROUP BY make, model, year, vehicle_style
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;


-- -------------------------------------------------------------
-- STEP 3: Inspect distinct values for categorical columns
-- -------------------------------------------------------------
SELECT DISTINCT engine_fuel_type  FROM car_features_raw ORDER BY 1;
SELECT DISTINCT transmission_type FROM car_features_raw ORDER BY 1;
SELECT DISTINCT driven_wheels     FROM car_features_raw ORDER BY 1;
SELECT DISTINCT vehicle_size      FROM car_features_raw ORDER BY 1;
SELECT DISTINCT vehicle_style     FROM car_features_raw ORDER BY 1;


-- -------------------------------------------------------------
-- STEP 4: Outlier check on MSRP and Engine HP
-- -------------------------------------------------------------
SELECT
    MIN(msrp)                                   AS min_msrp,
    MAX(msrp)                                   AS max_msrp,
    ROUND(AVG(msrp), 2)                         AS avg_msrp,
    COUNT(CASE WHEN msrp > 200000 THEN 1 END)   AS above_200k,
    COUNT(CASE WHEN msrp < 5000   THEN 1 END)   AS below_5k,
    MIN(engine_hp)                              AS min_hp,
    MAX(engine_hp)                              AS max_hp,
    ROUND(AVG(engine_hp), 1)                    AS avg_hp
FROM car_features_raw
WHERE msrp IS NOT NULL AND msrp > 0;


-- -------------------------------------------------------------
-- STEP 5: Insert cleaned data into car_features_clean
-- Cleaning rules applied:
--   - Exclude rows with NULL or zero/negative MSRP
--   - Exclude rows with NULL make or model
--   - De-duplicate: keep MIN(id) per make+model+year+style
--   - Trim whitespace from all text columns
--   - engine_fuel_type : lowercase, NULL becomes 'unknown'
--   - engine_hp        : NULL filled with avg of non-null values
--   - engine_cylinders : NULL becomes 4 (mode), cast to INTEGER
--   - transmission_type: uppercase, NULL becomes 'AUTOMATIC'
--   - number_of_doors  : NULL becomes 4, cast to INTEGER
--   - market_category  : NULL or empty becomes 'Unclassified'
--   - price_tier       : derived from MSRP (5 tier brackets)
--   - mpg_avg          : derived as (highway_mpg + city_mpg) / 2
-- -------------------------------------------------------------
INSERT INTO car_features_clean (
    make,
    model,
    year,
    engine_fuel_type,
    engine_hp,
    engine_cylinders,
    transmission_type,
    driven_wheels,
    number_of_doors,
    market_category,
    vehicle_size,
    vehicle_style,
    highway_mpg,
    city_mpg,
    popularity,
    msrp,
    price_tier,
    mpg_avg
)
SELECT
    TRIM(make),
    TRIM(model),
    year,

    CASE
        WHEN engine_fuel_type IS NULL OR TRIM(engine_fuel_type) = ''
            THEN 'unknown'
        ELSE LOWER(TRIM(engine_fuel_type))
    END,

    CASE
        WHEN engine_hp IS NULL
            THEN (
                SELECT ROUND(AVG(engine_hp), 1)
                FROM car_features_raw
                WHERE engine_hp IS NOT NULL
            )
        ELSE engine_hp
    END,

    CASE
        WHEN engine_cylinders IS NULL THEN 4
        ELSE CAST(engine_cylinders AS INTEGER)
    END,

    CASE
        WHEN transmission_type IS NULL OR TRIM(transmission_type) = ''
            THEN 'AUTOMATIC'
        ELSE UPPER(TRIM(transmission_type))
    END,

    TRIM(driven_wheels),

    CASE
        WHEN number_of_doors IS NULL THEN 4
        ELSE CAST(number_of_doors AS INTEGER)
    END,

    CASE
        WHEN market_category IS NULL OR TRIM(market_category) = ''
            THEN 'Unclassified'
        ELSE TRIM(market_category)
    END,

    TRIM(vehicle_size),
    TRIM(vehicle_style),
    highway_mpg,
    city_mpg,
    COALESCE(popularity, 0),
    msrp,

    CASE
        WHEN msrp < 20000                   THEN 'Budget'
        WHEN msrp BETWEEN 20000 AND 40000   THEN 'Mid-Range'
        WHEN msrp BETWEEN 40001 AND 70000   THEN 'Premium'
        WHEN msrp BETWEEN 70001 AND 150000  THEN 'Luxury'
        ELSE                                     'Ultra-Luxury'
    END,

    ROUND((highway_mpg + city_mpg) / 2.0, 1)

FROM car_features_raw
WHERE
    msrp IS NOT NULL
    AND msrp > 0
    AND make  IS NOT NULL AND TRIM(make)  != ''
    AND model IS NOT NULL AND TRIM(model) != ''
    AND year  IS NOT NULL
    AND id IN (
        SELECT MIN(id)
        FROM car_features_raw
        GROUP BY make, model, year, vehicle_style
    );


-- -------------------------------------------------------------
-- STEP 6: Verify final row count and summary statistics
-- -------------------------------------------------------------
SELECT
    COUNT(*)                        AS total_clean_rows,
    COUNT(DISTINCT make)            AS unique_brands,
    COUNT(DISTINCT vehicle_style)   AS unique_styles,
    COUNT(DISTINCT market_category) AS unique_market_categories,
    MIN(year)                       AS earliest_year,
    MAX(year)                       AS latest_year,
    ROUND(MIN(msrp), 0)             AS min_msrp,
    ROUND(MAX(msrp), 0)             AS max_msrp,
    ROUND(AVG(msrp), 2)             AS avg_msrp
FROM car_features_clean;


-- -------------------------------------------------------------
-- STEP 7: Create indexes AFTER data is loaded
-- Reason: Building on a populated table is faster than updating
-- them row-by-row during INSERT. Also avoids errors some SQL
-- clients throw when creating indexes on empty tables.
-- -------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_clean_make          ON car_features_clean(make);
CREATE INDEX IF NOT EXISTS idx_clean_year          ON car_features_clean(year);
CREATE INDEX IF NOT EXISTS idx_clean_msrp          ON car_features_clean(msrp);
CREATE INDEX IF NOT EXISTS idx_clean_market_cat    ON car_features_clean(market_category);
CREATE INDEX IF NOT EXISTS idx_clean_vehicle_style ON car_features_clean(vehicle_style);

-- Confirm indexes were created successfully
SELECT
    name     AS index_name,
    tbl_name AS on_table
FROM sqlite_master
WHERE type = 'index'
ORDER BY tbl_name, name;
