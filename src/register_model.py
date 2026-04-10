from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
from azure.identity import DefaultAzureCredential

subscription_id = "86c2aaee-2c2c-4ba5-9650-714b68528e97"
resource_group = "rg-60302085"
workspace_name = "Traffic_Accidents_Project"

# IMPORTANT: point to folder, not model.pkl
model_path = "azureml://datastores/workspaceblobstore/paths/azureml/d3d01206-9625-4241-894f-51e5c9b4fd08/model_output/"

ml_client = MLClient(
    DefaultAzureCredential(),
    subscription_id,
    resource_group,
    workspace_name
)

model = Model(
    path=model_path,
    name="us_accidents_rf_model",
    version="5",
    description="Final tuned Random Forest model for US Accidents severity prediction"
)

registered_model = ml_client.models.create_or_update(model)
print("Registered model:", registered_model.name, registered_model.version)