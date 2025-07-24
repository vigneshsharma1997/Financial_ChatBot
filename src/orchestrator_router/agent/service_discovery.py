import json 
import os 
from pathlib import Path 
 
 
def get_business_solutions()->dict: 
    """ 
    Load service configurations from JSON file 
    """ 
    file_path = Path("D:/code/propelops/my_project_template/ORCHESTRATOR_ROUTER/storage/mircoservice_url.json") 
    try: 
        with open(file_path,'r') as file: 
            return json.loads(file.read()) 
    except FileNotFoundError: 
        return {} 
    except json.JSONDecodeError: 
        return {} 
