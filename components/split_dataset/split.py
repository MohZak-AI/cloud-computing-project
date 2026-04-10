import argparse
import os
import time
import pandas as pd

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str, required=True)
    parser.add_argument("--train_out", type=str, required=True)
    parser.add_argument("--val_out", type=str, required=True)
    parser.add_argument("--test_out", type=str, required=True)
    parser.add_argument("--deploy_out", type=str, required=True)
    return parser.parse_args()

def main():
    args = parse_args()

    start = time.time()

    print("Loading dataset from:", args.input_data)

    # Azure ML mounts uri_folder inputs locally as a folder.
    # pandas can read a parquet folder if it contains parquet part files.
    df = pd.read_parquet(args.input_data)

    print("Initial rows:", len(df))
    print("Columns:", list(df.columns))

    # -------------------------
    # Select relevant columns
    # -------------------------
    selected_features = [
        "TemperatureF",
        "Wind_ChillF",
        "Humidity",
        "Visibilitymi",
        "Pressurein",
        "HourOfDay",
        "Month",
        "IsRushHour",
        "WeatherSeverityMapped",
        "AccidentYear"
    ]

    target = "Severity"
    time_col = "Start_Time"
    required_columns = selected_features + [target, time_col]
    df = df[required_columns].copy()

    # -------------------------
    # Type conversions
    # -------------------------
    df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")

    int_cols = ["Severity", "HourOfDay", "Month", "IsRushHour", "WeatherSeverityMapped", "AccidentYear"]
    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

    float_cols = ["TemperatureF", "Wind_ChillF", "Humidity", "Visibilitymi", "Pressurein"]
    for c in float_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # -------------------------
    # Drop missing required rows
    # -------------------------
    df = df.dropna(subset=required_columns).copy()

    # Convert nullable ints back to normal ints after dropna
    for c in int_cols:
        df[c] = df[c].astype(int)

    print("Rows after cleaning:", len(df))

    # -------------------------
    # Sort by time
    # -------------------------
    df = df.sort_values("Start_Time").reset_index(drop=True)

    # -------------------------
    # Deployment split = newest 10%
    # -------------------------
    total_rows = len(df)
    deploy_size = int(total_rows * 0.10)

    df_deploy = df.iloc[-deploy_size:].copy()
    df_remaining = df.iloc[:-deploy_size].copy()

    print("Remaining rows:", len(df_remaining))
    print("Deploy rows:", len(df_deploy))

    # -------------------------
    # Train / Val / Test split
    # 60 / 15 / 15 overall
    # On remaining 90% => 2/3, 1/6, 1/6
    # -------------------------
    df_remaining = df_remaining.sample(frac=1, random_state=42).reset_index(drop=True)

    n = len(df_remaining)
    train_end = int(n * 0.6667)
    val_end = train_end + int(n * 0.16665)

    train_df = df_remaining.iloc[:train_end].copy()
    val_df = df_remaining.iloc[train_end:val_end].copy()
    test_df = df_remaining.iloc[val_end:].copy()

    print("Train rows:", len(train_df))
    print("Val rows:", len(val_df))
    print("Test rows:", len(test_df))
    print("Deploy rows:", len(df_deploy))

    # -------------------------
    # Save outputs as parquet folders
    # -------------------------
    os.makedirs(args.train_out, exist_ok=True)
    os.makedirs(args.val_out, exist_ok=True)
    os.makedirs(args.test_out, exist_ok=True)
    os.makedirs(args.deploy_out, exist_ok=True)

    train_df.to_parquet(os.path.join(args.train_out, "data.parquet"), index=False)
    val_df.to_parquet(os.path.join(args.val_out, "data.parquet"), index=False)
    test_df.to_parquet(os.path.join(args.test_out, "data.parquet"), index=False)
    df_deploy.to_parquet(os.path.join(args.deploy_out, "data.parquet"), index=False)

    print("Splitting completed successfully.")
    print("Runtime seconds:", round(time.time() - start, 2))

if __name__ == "__main__":
    main()




    