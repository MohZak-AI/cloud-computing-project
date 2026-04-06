# Cloud Computing Project — US Accidents Analysis (Phase 1)

---

## 1. Objective

The objective of this project is to design and implement a reproducible data pipeline for analyzing the US Accidents (2016–2023) dataset. The pipeline prepares the data for machine learning tasks, specifically predicting accident severity based on temporal and weather-related features.

The focus of Phase 1 is on data engineering, including ingestion, transformation, storage, validation, and exploratory analysis.

---

## 2. Azure Environment

All components were deployed and executed in Microsoft Azure under:

**Resource Group:** `rg-60302085`

### Services Used:

* Azure Data Factory (ADF) → ETL pipeline
* Azure Data Lake Storage Gen2 → data storage
* Azure Databricks → validation, cleaning, EDA

---

## 3. Data Storage & Architecture

### Storage Account

**projecttraffic60302085**

### Data Organization

The project uses a structured data lake design:

* `raw/` → original data
* `processed/` → transformed data (ADF output)
* `curated/` → cleaned and analysis-ready data

### Medallion Architecture Alignment

| Layer  | Project Name |
| ------ | ------------ |
| Bronze | raw          |
| Silver | processed    |
| Gold   | curated      |

This layered approach ensures:

* traceability
* reproducibility
* separation of concerns

---

## 4. Data Ingestion

### Dataset

* File: `US_Accidents_March23.csv`
* Format: CSV
* Location: `raw/`

### Ingestion Details

* Mode: Batch
* Method: Azure Data Factory
* Schema inference: Enabled
* Schema drift: Enabled

### Data Refresh Strategy

The dataset is ingested using a one-time batch loading approach for Phase 1. The raw data is preserved without modification. Future improvements may include automated refresh using scheduled triggers.

---

## 5. ETL Pipeline (Azure Data Factory)

### Pipeline Details

* Pipeline Name: `accidents_processed_pipeline`
* Data Flow Name: `df_reviews_json_to_parquet_partitioned`

---

### Pipeline Workflow

#### 1. Source

* Reads CSV from:
  `raw/US_Accidents_March23.csv`
* Schema drift enabled

---

#### 2. Derived Column (Feature Engineering)

Created features:

* `accidentYear` → extracted year

* `hourOfDay` → extracted hour

* `month` → extracted month

* `isRushHour`:

  * Weekdays
  * 7–10 AM and 4–7 PM

* `weatherSeverityMapped`:

  * 1 → Clear/Fair
  * 2 → Cloudy/Fog
  * 3 → Rain
  * 4 → Severe

---

#### 3. Select Transformation (Column Standardization)

* Removed special characters using regex
* Fixed issues with:

  * spaces
  * parentheses
  * symbols
* Ensured compatibility with Parquet

---

#### 4. Sink

* Format: Parquet
* Location: `processed/accidents/`
* Partition column: `accidentYear`
* Schema drift enabled

---

### Output Structure

```text
processed/accidents/
  accidentYear=2016/
  accidentYear=2017/
  accidentYear=2018/
```

---

## 6. Data Cleaning (Databricks)

A Databricks notebook (`01_load_and_clean_accidents`) was used to refine the processed dataset into a curated layer.

### Cleaning Steps

* Converted:

  * `Start_Time` → timestamp

* Cast columns to integer:

  * accidentYear
  * hourOfDay
  * month
  * isRushHour
  * weatherSeverityMapped

* Removed duplicates

* Removed rows with missing key fields:

  * Start_Time
  * Severity
  * Weather_Condition

* Filled missing categorical values:

  * City → "Unknown"

### Output

Saved to:

```text
curated/accidents_features_v1/
```

---

## 7. Data Validation

Validation was performed during ETL and Databricks steps:

* Verified schema correctness
* Checked missing values
* Ensured data types
* Range validation:

  * hourOfDay (0–23)
  * month (1–12)

This confirms dataset readiness.

---

## 8. Data Schema & Metadata

### Key Columns

| Column            | Type      |
| ----------------- | --------- |
| ID                | string    |
| Severity          | integer   |
| Start_Time        | timestamp |
| Weather_Condition | string    |

### Derived Features

| Feature               | Type    |
| --------------------- | ------- |
| accidentYear          | integer |
| hourOfDay             | integer |
| month                 | integer |
| isRushHour            | integer |
| weatherSeverityMapped | integer |

---

## 9. Data Lineage

```text
Raw (CSV)
   → ADF Pipeline (Transformation)
   → Processed (Parquet)
   → Databricks Cleaning
   → Curated Dataset
```

---

## 10. Feature Engineering

Features created:

* accidentYear → time trend
* hourOfDay → daily patterns
* month → seasonal patterns
* isRushHour → traffic intensity
* weatherSeverityMapped → weather impact

These features were selected based on their relevance to accident severity prediction.

---

## 11. Exploratory Data Analysis (EDA)

Performed using Databricks notebook (`03_eda_accidents`).

### Analysis Conducted

* Accidents by year
* Accidents by hour
* Rush vs non-rush hour
* Weather severity distribution
* Severity distribution

### Key Insights

* Accidents vary across years
* Peak accidents occur during specific hours
* Rush hour significantly impacts accident frequency
* Most accidents occur in mild weather
* Severity distribution is imbalanced

---

## 12. Data Organization & Performance

* Stored in Parquet format
* Partitioned by accidentYear

Benefits:

* faster queries
* efficient filtering
* scalable processing

---

## 13. Cataloging & Governance

Metadata and schema were analyzed using:

* Databricks notebook (`02_metadata_and_schema`)

This includes:

* schema inspection
* column types
* null analysis
* dataset statistics

---

## 14. Source Code (Reference Implementation)

A PySpark script (`etl_process.py`) is included in the `src/` folder.

Purpose:

* demonstrate transformation logic
* provide reproducibility
* allow local validation

The main ETL pipeline is implemented in Azure Data Factory.

---

## 15. Databricks Notebooks

Included in `src/`:

* `01_load_and_clean_accidents` → cleaning
* `02_metadata_and_schema` → schema analysis
* `03_eda_accidents` → exploratory analysis

These support validation and transparency.

---

## 16. System Architecture

The system consists of:

* Azure Data Lake Storage Gen2 → data storage
* Azure Data Factory → ETL pipeline
* Databricks → analysis and validation

Data flows from raw to processed to curated layers.

---

## 17. Reproducibility

The pipeline is fully reproducible and can be re-executed using Azure Data Factory and Databricks notebooks to produce consistent results.

---

## 18. Assumptions

* Rush hour defined as peak traffic times
* Weather severity based on condition categories
* Time and weather impact accident likelihood

---

## 19. Phase 1 Status

### Completed

* Azure setup
* Data ingestion
* ETL pipeline
* Feature engineering
* Data cleaning
* Metadata analysis
* EDA

### Next Phase

* Machine learning model
* evaluation
* deployment

---

## 20. Summary

Phase 1 successfully establishes a complete data pipeline that transforms raw accident data into a structured, validated, and analysis-ready dataset.

The system is scalable, reproducible, and ready for machine learning tasks in Phase 2.
