US Accidents Severity Prediction Project – Phase 2 

## 1. Introduction

This report presents a fully detailed explanation of Phase 2 of the US Accidents machine learning project. The main objective is to design a complete machine learning pipeline that goes beyond simple model training. This includes data preparation, feature engineering, model comparison, hyperparameter tuning, deployment, and automation using Azure DevOps. The entire system is designed to be scalable, reproducible, and aligned with real-world industry practices in machine learning engineering.

## 2. Architecture and System Design

The system follows a layered cloud architecture using Azure services. Data is first ingested and processed using Azure Data Factory. It is then stored in Azure Data Lake in three layers: raw, processed, and curated. The curated layer is used as input to Azure Machine Learning pipelines. Each stage of the ML lifecycle is implemented using modular Azure ML components, ensuring reusability and clear separation of concerns. This architecture ensures that the pipeline can be extended easily in the future.

## 3. Data Preparation and Feature Engineering

The dataset contains millions of accident records, making preprocessing a critical step. Data cleaning includes handling missing values, converting data types, and ensuring consistency across features. Feature engineering focuses on extracting meaningful variables that impact accident severity. For example, HourOfDay captures time-based patterns, while IsRushHour highlights peak traffic periods. WeatherSeverityMapped simplifies complex weather conditions into numeric categories. These transformations help the model learn meaningful patterns from the data.

## 4. Data Splitting Strategy

A custom data splitting component was implemented to divide the dataset into train, validation, test, and deployment sets. Unlike random splitting, a time-based approach was used to avoid data leakage. This ensures that the model is evaluated on future-like data, which better reflects real-world deployment conditions. This design choice improves the reliability of the evaluation results.

## 5. Model Development and Comparison

Multiple models were implemented to explore different approaches. Logistic Regression was used as a baseline model, providing a simple linear perspective. Random Forest was introduced as a more powerful non-linear model capable of capturing complex relationships. A neural network was also tested to explore deep learning approaches. Each model was evaluated carefully to understand its strengths and weaknesses.

## 6. Evaluation Strategy

Evaluation metrics were carefully selected to handle class imbalance. Accuracy alone was not sufficient, as it can be misleading when one class dominates the dataset. Therefore, weighted F1-score and balanced accuracy were used as primary metrics. Confusion matrices were also analyzed to understand how each model performs across different severity levels.

## 7. Hyperparameter Tuning

Hyperparameter tuning was performed using Azure ML sweep jobs. This process automates the search for optimal model parameters. A random search strategy was used to explore different configurations. The tuning process significantly improved model performance, demonstrating the importance of proper optimization in machine learning workflows.

## 8. Final Model Selection

The tuned Random Forest model was selected as the final model. It achieved the best balance between performance and generalization. Compared to other models, it handled class imbalance more effectively and produced more reliable predictions across all classes.

## 9. Deployment and Inference

The final model was deployed using Azure ML managed online endpoints. A scoring script was developed to handle incoming requests, apply preprocessing, and generate predictions. The endpoint was tested using sample inputs and returned valid predictions, confirming that the deployment pipeline is functioning correctly.

## 10. MLOps and Automation

Azure DevOps was integrated to automate the training process. The pipeline installs dependencies, submits Azure ML jobs, and monitors execution. This ensures that the system is reproducible and supports continuous integration. Any future changes to the model can be automatically validated using this pipeline.

## 11. Discussion and Insights

The results highlight several important insights. First, model choice has a significant impact on performance, especially in imbalanced datasets. Second, evaluation metrics must be selected carefully to reflect real performance. Third, automation and reproducibility are essential for production-ready systems. Finally, combining multiple Azure services provides a powerful platform for building end-to-end machine learning solutions.

## 12. Conclusion

Phase 2 successfully demonstrates a complete machine learning lifecycle. The project integrates data engineering, model development, evaluation, deployment, and DevOps automation. The final system is robust, scalable, and aligned with industry best practices, making it a strong example of a production-ready ML pipeline.
