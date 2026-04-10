# US Accidents Severity Prediction Project — Phase 2 Report

## 1. Introduction
This phase focuses on building a complete end-to-end machine learning system using Azure services. The objective is to go beyond simple model training and implement a full pipeline including feature engineering, model comparison, hyperparameter tuning, deployment, and DevOps automation.

All work was performed under the Azure resource group **rg-60302085**.

---

## 2. System Architecture Overview
The system follows the **medallion architecture**:

Raw → Processed → Curated → Azure ML → Deployment

ADF Pipeline → Data Lake → Azure ML Components → Endpoint → DevOps

---

## 3. Data Preparation and Feature Engineering
Dataset: **US_Accidents_March23.csv**

### Features used:
- TemperatureF
- Wind_ChillF
- Humidity
- Visibilitymi
- Pressurein
- HourOfDay
- IsRushHour
- WeatherSeverityMapped

### Why these features:
They capture environmental and temporal conditions affecting accident severity.

---

## 4. Data Splitting Strategy
- Train: 60%
- Validation: 15%
- Test: 15%
- Deploy: 10%

Time-based split using `Start_Time` to avoid data leakage.

---

## 5. Model Development

### Logistic Regression
- Accuracy ≈ 0.20
- F1 ≈ 0.28
- Balanced Accuracy ≈ 0.37
→ Weak baseline

### Random Forest
- Initial F1 ≈ 0.52
→ Strong improvement

### Neural Network
- Accuracy ≈ 0.83
- Balanced Accuracy ≈ 0.25
→ Failed due to class imbalance

---

## 6. Evaluation Strategy
Metrics:
- Accuracy
- Weighted F1 (main)
- Balanced Accuracy
- Confusion Matrix

---

## 7. Hyperparameter Tuning
Using Azure ML Sweep Job.

Best parameters:
- n_estimators = 400
- max_depth = 25
- min_samples_split = 10
- min_samples_leaf = 4

Final Performance:
- F1 ≈ 0.72
- Balanced Accuracy ≈ 0.49
- Accuracy ≈ 0.69

---

## 8. Final Model Selection
Selected model: **Random Forest (tuned)**

Reasons:
- Highest F1 score
- Balanced predictions
- Stable results

---

## 9. Deployment
Deployed using Azure ML Endpoint.

Flow:
Input → Preprocessing → Model → Output

Example response:
```json
{"predictions": [1]}
```

---

## 10. Azure DevOps (MLOps)
Pipeline automates:
- Training job submission
- Logging
- Validation

---

## 11. Key Insights
1. Tree models outperform linear models
2. Accuracy is misleading in imbalanced data
3. Hyperparameter tuning is critical
4. Deployment validation is necessary
5. MLOps improves reliability

---

## 12. Conclusion
A full ML pipeline was successfully implemented including training, tuning, deployment, and automation. The tuned Random Forest model achieved strong performance and was deployed successfully.
