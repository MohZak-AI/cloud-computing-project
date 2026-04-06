### Supplementary PySpark Reference

#A supplementary PySpark script (`etl_process.py`) was retained in the repository as a reference implementation for local validation and reproducibility. 
# The script mirrors the core transformation logic of the Azure Data Factory pipeline, including timestamp conversion, temporal feature extraction, 
# weather severity mapping, and Parquet output generation.

#However, the final production ETL workflow for Phase 1 was implemented and executed in Azure Data Factory, not in PySpark.






from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, hour, dayofweek, month, year, to_timestamp

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("US_Accidents_ETL_Reference") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

# Azure Data Lake Storage Gen2 paths
# Final project storage account and containers
INPUT_PATH = "abfss://raw@projecttraffic60302085.dfs.core.windows.net/US_Accidents_March23.csv"
OUTPUT_PATH_PROCESSED = "abfss://processed@projecttraffic60302085.dfs.core.windows.net/accidents/"

# Optional local testing
# INPUT_PATH = "./US_Accidents_March23.csv"
# OUTPUT_PATH_PROCESSED = "./processed_accidents.parquet"

def preprocess_accidents(df):
    """
    Reference ETL logic aligned with the final ADF pipeline.
    This script is kept for local validation and reproducibility support.
    The main ETL pipeline was implemented in Azure Data Factory.
    """

    # Convert Start_Time to timestamp
    df = df.withColumn(
        "Start_Time",
        to_timestamp(col("Start_Time"), "yyyy-MM-dd HH:mm:ss")
    )

    # Derived features aligned with ADF pipeline
    df = df.withColumn("accidentYear", year(col("Start_Time")))
    df = df.withColumn("hourOfDay", hour(col("Start_Time")))
    df = df.withColumn("month", month(col("Start_Time")))

    # Rush hour: weekdays, 7-9 AM and 4-6 PM
    df = df.withColumn(
        "isRushHour",
        when(
            (dayofweek(col("Start_Time")).between(2, 6)) &
            (
                (col("hourOfDay").between(7, 9)) |
                (col("hourOfDay").between(16, 18))
            ),
            1
        ).otherwise(0)
    )

    # Weather severity mapping aligned with ADF logic
    df = df.withColumn(
        "weatherSeverityMapped",
        when(col("Weather_Condition").isin("Fair", "Clear"), 1)
        .when(col("Weather_Condition").isin("Cloudy", "Fog"), 2)
        .when(col("Weather_Condition").isin("Light Rain", "Rain"), 3)
        .otherwise(4)
    )

    return df

if __name__ == "__main__":
    print(f"Loading data from {INPUT_PATH}...")

    raw_df = spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(INPUT_PATH)

    print("Processing data...")
    processed_df = preprocess_accidents(raw_df)

    print(f"Saving Parquet output to {OUTPUT_PATH_PROCESSED}...")
    processed_df.write \
        .mode("overwrite") \
        .partitionBy("accidentYear") \
        .parquet(OUTPUT_PATH_PROCESSED)

    print("Reference ETL job completed successfully.")
    spark.stop()
