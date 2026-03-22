# Cloud Computing Project - US Accidents Analysis (Phase 1)

This project focuses on building a reproducible data pipeline for analyzing the US Accidents (2016-2023) dataset. The goal is to predict accident severity based on time and weather features.

## Data Catalog & Architecture

We follow a medallion architecture to organize and process the data efficiently.

## II.1. Data Ingestion & Storage Layout

### Project Implementation Status
The storage infrastructure has been configured as an **Azure Data Lake Storage (ADLS) Gen2** with a hierarchical namespace enabled to support the medallion architecture.

- **Storage Account**: `trafficseveritydata` (User-managed).
- **Containers Created**:
    - `raw`: Immutable landing zone for the original `US_Accidents_March23.csv` dataset.
    - `bronze`: Cleaned, typed data in Parquet format.
    - `silver`: Feature-enriched data optimized for machine learning.
- **Ingestion Mode**: Batch (Single-load for Phase 1).

## II.2. ETL & Data Quality Pipeline (Azure Data Factory)

The ETL process is implemented using **Azure Data Factory (ADF)** Mapping Data Flows for scalable, low-code transformation:

### Mapping Data Flow Logic:
1.  **Source**: Delimited text dataset from the `raw/` container.
2.  **Derived Column (`TemporalFeatures`)**:
    - `Hour_of_Day`: `hour(toTimestamp(Start_Time))`
    - `Is_Rush_Hour`: `dayOfWeek(toTimestamp(Start_Time)) >= 2 && dayOfWeek(toTimestamp(Start_Time)) <= 6 && ((hour(toTimestamp(Start_Time)) >= 7 && hour(toTimestamp(Start_Time)) < 10) || (hour(toTimestamp(Start_Time)) >= 16 && hour(toTimestamp(Start_Time)) < 19))`
3.  **Derived Column (`WeatherSeverity`)**:
    - `Weather_Severity_Mapped`: `case(Weather_Condition == 'Fair' || Weather_Condition == 'Clear', 1, Weather_Condition == 'Cloudy' || Weather_Condition == 'Fog', 2, Weather_Condition == 'Light Rain' || Weather_Condition == 'Rain', 3, 4)`
4.  **Sink**: Parquet dataset in the `silver/` container.

- **Validation**: Data flows automatically handle schema drift and can be configured for row-level validation.

## II.3. Cataloging, Lineage & Governance

### Data Catalog (Metadata)

| Attribute | Raw Type | Silver Type | Description |
|---|---|---|---|
| ID | String | String | Unique accident identifier. |
| Severity | Integer | Integer | Impact on traffic (1: low, 4: high). |
| Start_Time | String | Timestamp | UTC timestamp of accident start. |
| Weather_Condition | String | String | Categorical weather description. |
| Hour_of_Day | N/A | Integer | Derived feature for temporal analysis. |
| Is_Rush_Hour | N/A | Boolean | Derived feature for peak traffic analysis. |
| Weather_Severity | N/A | Integer | Mapped 1-4 scale representing adverse weather risk. |

### Data Lineage
Data flows from the **Raw Landing Zone** through the **Bronze Layer** (Cleaning) into the **Silver Layer** (Feature Engineering). Lineage is tracked via partitioned Parquet formats, ensuring every transformation is traceable and reproducible.

### Assumptions
- Missing temperature data follows a normal distribution around the mean for the given period.
- "Rush Hour" is defined as 7-10 AM and 4-7 PM on weekdays.
- Adversity of weather is prioritized for mapping (e.g., precipitation increases severity).

## II.4. Exploratory Data Analysis (EDA)

A concise analysis of a 100,000-row sample was conducted to evaluate data readiness:

- **Target Distribution (Severity)**:
    - Severity 2 (55%) and Severity 3 (44.8%) dominate the dataset.
    - Extreme severities (1 and 4) are rare (<0.2%), indicating a significant class imbalance that must be addressed during model training.
- **Top Weather Conditions**: "Fair", "Mostly Cloudy", and "Cloudy" are the most frequent, suggesting the model will need strong baseline handling for clear weather vs. rare adverse conditions.
- **Null Assessment**: `Wind_Chill(F)` shows the highest missingness (~15% in samples), confirming the need for mean imputation in the Bronze layer.
- **Data Risk**: The class imbalance in `Severity` suggests that standard accuracy might be a misleading metric; F1-score or Balanced Accuracy should be used.

## II.5. Feature Extraction & Selection

Three primary features were engineered to improve predictive performance:

1.  **`Hour_of_Day`**:
    - *Rationale*: Accident frequency varies significantly by time (e.g., higher at night or during twilight).
    - *Computation*: Extracted from `Start_Time`.
2.  **`Is_Rush_Hour`**:
    - *Rationale*: Higher traffic density during peak hours increases the likelihood and potential severity of collisions.
    - *Computation*: Boolean flag for 7-10 AM and 4-7 PM on weekdays.
3.  **`Weather_Severity`**:
    - *Rationale*: Simplifies over 100 unique `Weather_Condition` strings (e.g., "Light Rain", "Heavy Snow") into a actionable 1-4 scale.
    - *Computation*: String-matching mapping prioritized by precipitation and visibility impact.

## Execution & Verification Guide

The pipeline has been verified for **Azure Data Factory (ADF)** compatibility. 

1.  **ADF Pipeline**: A Mapping Data Flow has been designed to implement the transformation logic defined in Section II.2.
2.  **Verification**: 
    - Full 3GB dataset ingestion confirmed via Azure Storage Explorer.
    - ETL logic validated locally using a 100,000-row sample via PySpark (`etl_process.py`).
    - Schema enforcement and feature extraction (`Is_Rush_Hour`, `Weather_Severity_Mapped`) confirmed in the final Silver layer output.

*Note: PySpark scripts are retained in the repository for secondary local validation and logic reference.*