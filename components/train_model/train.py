import argparse
import os
import time
import joblib
import mlflow
import azureml.mlflow
import pandas as pd

from sklearn.impute import SimpleImputer
#from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    balanced_accuracy_score,
    confusion_matrix
)

scaler = None
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_data", type=str, required=True)
    parser.add_argument("--val_data", type=str, required=True)
    parser.add_argument("--test_data", type=str, required=True)
    parser.add_argument("--class_weight", type=str, default="balanced_subsample")
    parser.add_argument("--n_estimators", type=int, default=400)
    parser.add_argument("--max_depth", type=int, default=25)
    parser.add_argument("--min_samples_split", type=int, default=10)
    parser.add_argument("--min_samples_leaf", type=int, default=4)
    parser.add_argument("--max_features", type=str, default="sqrt")
    parser.add_argument("--output", type=str, required=True)


    
    return parser.parse_args()

def load_data(path):
    if os.path.isdir(path):
        parquet_file = os.path.join(path, "data.parquet")
        if os.path.exists(parquet_file):
            return pd.read_parquet(parquet_file)
    return pd.read_parquet(path)

def evaluate(model, X, y, split_name):
    preds = model.predict(X)

    acc = accuracy_score(y, preds)
    bal_acc = balanced_accuracy_score(y, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, preds, average="weighted", zero_division=0
    )

    mlflow.log_metric(f"{split_name}_accuracy", acc)
    mlflow.log_metric(f"{split_name}_balanced_accuracy", bal_acc)
    mlflow.log_metric(f"{split_name}_precision_weighted", precision)
    mlflow.log_metric(f"{split_name}_recall_weighted", recall)
    mlflow.log_metric(f"{split_name}_f1_weighted", f1)

    print(f"{split_name} accuracy: {acc:.4f}")
    print(f"{split_name} balanced accuracy: {bal_acc:.4f}")
    print(f"{split_name} weighted precision: {precision:.4f}")
    print(f"{split_name} weighted recall: {recall:.4f}")
    print(f"{split_name} weighted f1: {f1:.4f}")

    print(f"{split_name} confusion matrix:")
    print(confusion_matrix(y, preds))

    return {
        "accuracy": acc,
        "balanced_accuracy": bal_acc,
        "precision_weighted": precision,
        "recall_weighted": recall,
        "f1_weighted": f1
    }

def main():
    args = parse_args()
    start_time = time.time()

    mlflow.start_run()

    print("Loading datasets...")
    train_df = load_data(args.train_data)
    val_df = load_data(args.val_data)
    test_df = load_data(args.test_data)

    print("Train rows:", len(train_df))
    print("Val rows:", len(val_df))
    print("Test rows:", len(test_df))

    feature_cols = [
        "TemperatureF",
        "Wind_ChillF",
        "Humidity",
        "Visibilitymi",
        "Pressurein",
        "HourOfDay",
        "IsRushHour",
        "WeatherSeverityMapped",
    ]

    target_col = "Severity"

    required_cols = feature_cols + [target_col]
    print(required_cols, flush=True)
    for df_name, df in [("train", train_df), ("val", val_df), ("test", test_df)]:
        print(df.columns.tolist())
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            raise RuntimeError(f"Missing columns in {df_name} dataset: {missing}")
    
    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col].copy()

    X_val = val_df[feature_cols].copy()
    y_val = val_df[target_col].copy()

    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_col].copy()

    # Impute missing numeric values
    imputer = SimpleImputer(strategy="median")
    X_train = imputer.fit_transform(X_train)
    X_val = imputer.transform(X_val)
    X_test = imputer.transform(X_test)


        
    
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
        min_samples_split=args.min_samples_split,
        min_samples_leaf=args.min_samples_leaf,
        max_features=args.max_features,
        class_weight=args.class_weight,
        random_state=42,
        n_jobs=-1
    )

    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("n_estimators", args.n_estimators)
    mlflow.log_param("max_depth", args.max_depth)
    mlflow.log_param("min_samples_split", args.min_samples_split)
    mlflow.log_param("min_samples_leaf", args.min_samples_leaf)
    mlflow.log_param("max_features", args.max_features)
    mlflow.log_param("class_weight", args.class_weight)
    mlflow.log_param("feature_count", len(feature_cols))
    mlflow.log_param("features", ",".join(feature_cols))
    



    print("Training model...")
    model.fit(X_train, y_train)

    print("Evaluating...")
    train_metrics = evaluate(model, X_train, y_train, "train")
    val_metrics = evaluate(model, X_val, y_val, "val")
    test_metrics = evaluate(model, X_test, y_test, "test")

    os.makedirs(args.output, exist_ok=True)

    model_path = os.path.join(args.output, "model.pkl")
    imputer_path = os.path.join(args.output, "imputer.pkl")

    joblib.dump(model, model_path)
    joblib.dump(imputer, imputer_path)

    mlflow.log_artifact(model_path)
    mlflow.log_artifact(imputer_path)

    runtime = time.time() - start_time
    mlflow.log_metric("training_runtime_seconds", runtime)

    print("Training completed successfully.")
    print("Runtime seconds:", round(runtime, 2))

    mlflow.end_run()

if __name__ == "__main__":
    main()
