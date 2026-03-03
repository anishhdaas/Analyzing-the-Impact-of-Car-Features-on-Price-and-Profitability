-- FILE: sql/04_business_insights.sql
-- PURPOSE: Business-level queries for all 5 project tasks
-- RUN ORDER: Step 4 of 4

-- TASK 1A: Popularity by market category (pivot table)
SELECT
    market_category,
    COUNT(*)                  AS num_car_models,
    ROUND(AVG(popularity), 0) AS avg_popularity,
    MIN(popularity)           AS min_popularity,
    MAX(popularity)           AS max_popularity,
    ROUND(AVG(msrp), 0)       AS avg_msrp
FROM car_features_clean
GROUP BY market_category
ORDER BY avg_popularity DESC;

-- TASK 1B: Model count + popularity for combo chart
SELECT
    market_category,
    COUNT(*)                  AS num_models,
    ROUND(AVG(popularity), 0) AS avg_popularity
FROM car_features_clean
GROUP BY market_category
ORDER BY num_models DESC
LIMIT 15;

-- TASK 2: Engine HP vs MSRP scatter data
SELECT
    ROUND(engine_hp / 50.0) * 50 AS hp_bucket,
    COUNT(*)                     AS count,
    ROUND(AVG(msrp), 0)          AS avg_msrp,
    ROUND(MIN(msrp), 0)          AS min_msrp,
    ROUND(MAX(msrp), 0)          AS max_msrp
FROM car_features_clean
WHERE engine_hp IS NOT NULL
GROUP BY hp_bucket
ORDER BY hp_bucket;

-- TASK 2: Pearson correlation - Engine HP vs MSRP
SELECT
    ROUND(
        (AVG(engine_hp * msrp) - AVG(engine_hp) * AVG(msrp))
        /
        (
            SQRT(AVG(engine_hp * engine_hp) - AVG(engine_hp) * AVG(engine_hp))
            *
            SQRT(AVG(msrp * msrp) - AVG(msrp) * AVG(msrp))
        ),
    4) AS pearson_r_hp_vs_msrp
FROM car_features_clean
WHERE engine_hp IS NOT NULL;

-- TASK 3: Feature averages by price tier (supports regression)
SELECT
    price_tier,
    COUNT(*)                       AS count,
    ROUND(AVG(engine_hp), 1)       AS avg_hp,
    ROUND(AVG(engine_cylinders), 1) AS avg_cylinders,
    ROUND(AVG(highway_mpg), 1)     AS avg_highway_mpg,
    ROUND(AVG(popularity), 0)      AS avg_popularity,
    ROUND(AVG(msrp), 0)            AS avg_msrp
FROM car_features_clean
GROUP BY price_tier
ORDER BY AVG(msrp);

-- TASK 3: Transmission type influence on MSRP
SELECT
    transmission_type,
    COUNT(*)            AS count,
    ROUND(AVG(msrp), 0) AS avg_msrp,
    ROUND(MIN(msrp), 0) AS min_msrp,
    ROUND(MAX(msrp), 0) AS max_msrp
FROM car_features_clean
GROUP BY transmission_type
ORDER BY avg_msrp DESC;

-- TASK 4A: All manufacturers ranked by average MSRP
SELECT
    make,
    COUNT(*)                   AS model_count,
    ROUND(AVG(msrp), 0)        AS avg_msrp,
    ROUND(MIN(msrp), 0)        AS min_msrp,
    ROUND(MAX(msrp), 0)        AS max_msrp,
    ROUND(AVG(engine_hp), 1)   AS avg_hp,
    ROUND(AVG(highway_mpg), 1) AS avg_highway_mpg,
    ROUND(AVG(popularity), 0)  AS avg_popularity
FROM car_features_clean
GROUP BY make
ORDER BY avg_msrp DESC;

-- TASK 4B: Top 15 highest average MSRP brands
SELECT
    make,
    ROUND(AVG(msrp), 0) AS avg_msrp,
    COUNT(*)            AS model_count
FROM car_features_clean
GROUP BY make
ORDER BY avg_msrp DESC
LIMIT 15;

-- TASK 4C: Top 15 lowest average MSRP brands (min 10 models)
SELECT
    make,
    ROUND(AVG(msrp), 0) AS avg_msrp,
    COUNT(*)            AS model_count
FROM car_features_clean
GROUP BY make
HAVING model_count >= 10
ORDER BY avg_msrp ASC
LIMIT 15;

-- TASK 5A: Cylinders vs highway MPG scatter data
SELECT
    engine_cylinders,
    COUNT(*)                   AS count,
    ROUND(AVG(highway_mpg), 2) AS avg_highway_mpg,
    ROUND(AVG(city_mpg), 2)    AS avg_city_mpg,
    ROUND(AVG(mpg_avg), 2)     AS avg_combined_mpg
FROM car_features_clean
WHERE engine_cylinders IS NOT NULL
GROUP BY engine_cylinders
ORDER BY engine_cylinders;

-- TASK 5B: Pearson correlation - cylinders vs highway MPG
SELECT
    ROUND(
        (AVG(engine_cylinders * highway_mpg) - AVG(engine_cylinders) * AVG(highway_mpg))
        /
        (
            SQRT(AVG(engine_cylinders * engine_cylinders) - AVG(engine_cylinders) * AVG(engine_cylinders))
            *
            SQRT(AVG(highway_mpg * highway_mpg) - AVG(highway_mpg) * AVG(highway_mpg))
        ),
    4) AS pearson_r_cylinders_vs_highway_mpg
FROM car_features_clean
WHERE engine_cylinders IS NOT NULL;

-- DASHBOARD TASK 1: MSRP distribution by Brand and Body Style
SELECT
    make,
    vehicle_style,
    COUNT(*)             AS count,
    ROUND(SUM(msrp), 0)  AS total_msrp,
    ROUND(AVG(msrp), 0)  AS avg_msrp,
    ROUND(MIN(msrp), 0)  AS min_msrp,
    ROUND(MAX(msrp), 0)  AS max_msrp
FROM car_features_clean
GROUP BY make, vehicle_style
ORDER BY make, avg_msrp DESC;

-- DASHBOARD TASK 2: Highest and lowest avg MSRP by brand and body style
SELECT
    make,
    vehicle_style,
    COUNT(*)            AS count,
    ROUND(AVG(msrp), 0) AS avg_msrp
FROM car_features_clean
GROUP BY make, vehicle_style
ORDER BY avg_msrp DESC;

-- DASHBOARD TASK 3: Transmission type effect on MSRP by body style
SELECT
    transmission_type,
    vehicle_style,
    COUNT(*)            AS count,
    ROUND(AVG(msrp), 0) AS avg_msrp,
    ROUND(MIN(msrp), 0) AS min_msrp,
    ROUND(MAX(msrp), 0) AS max_msrp
FROM car_features_clean
GROUP BY transmission_type, vehicle_style
ORDER BY transmission_type, avg_msrp DESC;

-- DASHBOARD TASK 4: Fuel efficiency trend by year and body style
SELECT
    year,
    vehicle_style,
    ROUND(AVG(highway_mpg), 2) AS avg_highway_mpg,
    ROUND(AVG(city_mpg), 2)    AS avg_city_mpg,
    ROUND(AVG(mpg_avg), 2)     AS avg_combined_mpg,
    COUNT(*)                   AS count
FROM car_features_clean
GROUP BY year, vehicle_style
ORDER BY year, vehicle_style;

-- DASHBOARD TASK 5: HP, MPG, Price by Brand for bubble chart
-- Only brands with 5 or more models included
SELECT
    make,
    ROUND(AVG(engine_hp), 1)   AS avg_hp,
    ROUND(AVG(highway_mpg), 2) AS avg_highway_mpg,
    ROUND(AVG(city_mpg), 2)    AS avg_city_mpg,
    ROUND(AVG(msrp), 0)        AS avg_msrp,
    COUNT(*)                   AS model_count
FROM car_features_clean
GROUP BY make
HAVING model_count >= 5
ORDER BY avg_msrp DESC;
