import os

structure = {
    "src" : {
        "orchestrator_router":{
            "agent":{},
            "app":{},
            "utils":{},
            "common":{},
            "storage":{},
            "test":{},
            "main.py":None,
            "requirments.txt":None,
            "DockerFile":None
        },
        "kpi_agent":{
            "agent":{},
            "app":{},
            "utils":{},
            "common":{},
            "storage":{},
            "test":{},
            "main.py":None,
            "requirments.txt":None,
            "DockerFile":None
        },
        "rag_agent":{
            "agent":{
                "__init__.py":None
            },
            "app":{
                "__init.py":None,
                "app.py":None
            },
            "utils":{
                "__init.py":None,
                "config.py":None,
                "logging.py":None,
                "utils.py":None
            },
            "common":{
                "__init__.py":None,
                "database_connection.py":None,
                "llm_connection.py":None,
                "sql_constants.py":None,
                "vector_db_config.py":None,
                "vector_db_connection.py":None
            },
            "storage":{},
            "test":{},
            "__init__.py":None,
            "main.py":None,
            "requirments.txt":None,
            "DockerFile":None
        }
    },
    "enviroments":{},
    "iac":{}
}

def create_struct(base_path,struct):
    for name,content in struct.items():
        path = os.path.join(base_path,name)
        if content is None:
            with open(path,"w") as f:
                f.write("")
        else:
            os.makedirs(path,exist_ok=True)
            create_struct(path,content)

base_directory = "."
create_struct(base_directory,structure)
print("Directory created successfully.")