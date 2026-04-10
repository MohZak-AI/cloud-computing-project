import json
import os
import joblib
import pandas as pd

model = None
imputer = None

feature_cols = [
    "TemperatureF",
    "Wind_ChillF",
    "Humidity",
    "Visibilitymi",
    "Pressurein",
    "HourOfDay",
    "IsRushHour",
    "WeatherSeverityMapped"
]

def init():
    global model, imputer

    model_dir = os.getenv("AZUREML_MODEL_DIR")
    if not model_dir:
        raise EnvironmentError("AZUREML_MODEL_DIR is not set")

    model_path = os.path.join(model_dir, "model_output", "model.pkl")
    imputer_path = os.path.join(model_dir, "model_output", "imputer.pkl")

    # 🔴 Explicit file checks
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"model.pkl not found at: {model_path}")

    if not os.path.exists(imputer_path):
        raise FileNotFoundError(f"imputer.pkl not found at: {imputer_path}")

    # Load artifacts
    model = joblib.load(model_path)
    imputer = joblib.load(imputer_path)


def run(raw_data):
    try:
        data = json.loads(raw_data)

        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)

        missing = [c for c in feature_cols if c not in df.columns]
        if missing:
            return {"error": f"Missing required columns: {missing}"}

        X = df[feature_cols].copy()
        X = imputer.transform(X)
        preds = model.predict(X).tolist()

        return {"predictions": preds}

    except Exception as e:
        return {"error": str(e)}