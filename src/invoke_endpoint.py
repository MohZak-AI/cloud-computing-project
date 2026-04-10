import json
import requests
import subprocess

# Get endpoint key
endpoint_name = "us-accidents-endpoint"

scoring_uri = subprocess.check_output(
    ["az", "ml", "online-endpoint", "show", "--name", endpoint_name, "--query", "scoring_uri", "-o", "tsv"],
    text=True
).strip()

key = subprocess.check_output(
    ["az", "ml", "online-endpoint", "get-credentials", "--name", endpoint_name, "--query", "primaryKey", "-o", "tsv"],
    text=True
).strip()

sample = [
    {
        "TemperatureF": 72.0,
        "Wind_ChillF": 70.0,
        "Humidity": 55.0,
        "Visibilitymi": 10.0,
        "Pressurein": 29.9,
        "HourOfDay": 8,
        "IsRushHour": 1,
        "WeatherSeverityMapped": 1
    }
]

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {key}"
}

response = requests.post(scoring_uri, headers=headers, data=json.dumps(sample))

print("Status code:", response.status_code)
print("Response:", response.text)