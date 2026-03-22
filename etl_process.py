from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, hour, dayofweek, udf
from pyspark.sql.types import IntegerType, TimestampType, BooleanType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("US_Accidents_ETL") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

# File paths (Azure Data Lake Storage Gen2 format)
# Account: trafficseverity, Container: raw/bronze/silver
INPUT_PATH = "abfss://raw@trafficseverity.dfs.core.windows.net/US_Accidents_March23.csv"
OUTPUT_PATH_SILVER = "abfss://silver@trafficseverity.dfs.core.windows.net/us_accidents_silver.parquet"

# For local verification, uncomment the following:
# INPUT_PATH = "./US_Accidents_March23.csv"
# OUTPUT_PATH_SILVER = "./silver_us_accidents.parquet"

def preprocess_accidents(df):
    """
    Cleans and transforms US Accidents dataset.
    - Handles missing values for Temperature and Wind Chill.
    - Converts Start_Time to timestamp.
    - Extracts features: Hour_of_Day, Is_Rush_Hour, Weather_Severity.
    """
    
    # 1. Convert Start_Time to Timestamp
    df = df.withColumn("Start_Time", col("Start_Time").cast(TimestampType()))

    # 2. Handle missing values: Fill with mean (approximate for simplicity in script)
    # Note: In production, you might group by region or season for more accurate imputation.
    temp_mean = df.selectExpr("avg(`Temperature(F)`)").collect()[0][0]
    wind_chill_mean = df.selectExpr("avg(`Wind_Chill(F)`)").collect()[0][0]
    
    df = df.fillna({"Temperature(F)": temp_mean, "Wind_Chill(F)": wind_chill_mean})

    # 3. Feature Extraction: Hour_of_Day
    df = df.withColumn("Hour_of_Day", hour(col("Start_Time")))

    # 4. Feature Extraction: Is_Rush_Hour (Boolean)
    # Define Rush Hour: Weekdays (2-6) between 7-10 AM and 4-7 PM
    df = df.withColumn("Is_Rush_Hour", 
        (dayofweek(col("Start_Time")).between(2, 6)) & 
        ((col("Hour_of_Day").between(7, 9)) | (col("Hour_of_Day").between(16, 18)))
    )

    # 5. Weather Severity Mapping (1-4)
    # 1: Clear/Fair, 2: Cloudy/Overcast/Fog, 3: Light Precipitation/T-Storms, 4: Heavy Precipitation/Extreme
    weather_severity_mapping = {
        "Fair": 1, "Clear": 1, "Scattered Clouds": 1, "Partly Cloudy": 1,
        "Mostly Cloudy": 2, "Cloudy": 2, "Overcast": 2, "Fog": 2, "Haze": 2,
        "Light Rain": 3, "Light Snow": 3, "Light Drizzle": 3, "Rain": 3, "Snow": 3, "T-Storm": 3, "Thunder in the Vicinity": 3,
        "Heavy Rain": 4, "Heavy Snow": 4, "Thunderstorm": 4, "Heavy T-Storm": 4, "Tornado": 4
    }

    # Define a UDF for mapping (more flexible for complex mappings)
    @udf(returnType=IntegerType())
    def map_weather_severity(condition):
        if not condition: return 1 # Default to 1 if unknown
        return weather_severity_mapping.get(condition, 2) # Default to 2 for unknown but present

    df = df.withColumn("Weather_Severity_Mapped", map_weather_severity(col("Weather_Condition")))

    return df

if __name__ == "__main__":
    print(f"Loading data from {INPUT_PATH}...")
    
    # Read CSV with schema inference for simplicity in this script
    raw_df = spark.read.option("header", "true").option("inferSchema", "true").csv(INPUT_PATH)
    
    print("Processing data...")
    silver_df = preprocess_accidents(raw_df)
    
    print(f"Saving optimized Parquet to {OUTPUT_PATH_SILVER}...")
    silver_df.write.mode("overwrite").parquet(OUTPUT_PATH_SILVER)
    
    print("ETL Job Completed successfully.")
    spark.stop()
