from typing import List
import requests
import json

headers = {
        "Authorization": "Bearer temp and local anyway",
        "Content-Type": "application/json"
}

def get_model(model_id: str, model_type: str, model_name:str, vendor_name: str ) -> List[dict]:
    """Gets all models present in the table.

        Args: model_id (Optional[str]): model_id to filter to, if provided model_type (Optional[str]): model_type to filter to, if provided model_name (Optional[str]): model_name to filter to, if provided vendor_name (Optional[str]): vendor_name to filter to, if provided db (Session): the current database session user_info (UserInfo): the current user enforcer

        Returns: List[dict]: A list of every model object in the table.
    """
    response = requests.get("http://localhost:8081/dms/api/model", headers=headers)
    return response.json()