import uvicorn 
from fastapi import FastAPI,HTTPException,status 
from fastapi.middleware.cors import CORSMiddleware 
from pydantic import BaseModel 
from utils.logger import get_logger 
from common.LLM_Client import llm_model 
from utils.config import generate_task_id,generate_global_chat_id 
from common.Azure_MySQL_Connector import insert_session_id_chat_id_to_db 
from typing import Any,Dict,Literal,Optional 
import httpx 
from langchain_core.output_parsers import StrOutputParser 
from agent.agent_routing import AgentRouting 
from agent.microservice_task_orchestrator import trigger_selected_microservices 
 
logger = get_logger() 
 
app = FastAPI() 
 
class QueryRequest(BaseModel): 
    user_query : str 
 
class TaskResponse(BaseModel): 
    task_id: str 
    chat_id: str 
    session_id: str 
 
class ChatRequest(BaseModel): 
    session_id:str 
    user_query:str 
    translate_query : Optional[bool] = False 
    method : Optional[Literal["llm","keyword"]] = "llm" 
 
app.add_middleware( 
    CORSMiddleware, 
    allow_origins = ["*"], 
    allow_credentials = False, 
    allow_methods = ["GET","POST","OPTIONS"], 
    allow_headers = ["*"] 
) 
 
@app.post("/core-app/orchestrator/chat",response_model=TaskResponse) 
async def process_user_request(chat_request:ChatRequest): 
    llm = llm_model() 
    try : 
        parent_task_id = generate_task_id() 
        prompt = f""" 
                Based on the user query: "{chat_request.user_query}", generate a **single, short folder name** (2-3 words only).  
 
                Return ONLY the folder name as plain text. Do NOT return a list, explanation, or formatting. 
            """ 
 
        llm_response = llm.invoke(prompt) 
        folder_name = llm_response.content.strip() 
        print(folder_name)  
        print(llm_response) 
         
        aggregrated_db_payload = { 
            "session_id" : chat_request.session_id, 
            "source_agent":"combined_agents", 
            "user_query":chat_request.user_query, 
            "chat_id" : generate_global_chat_id(), 
            "question_title":folder_name 
        } 
        # insert_session_id_chat_id_to_db(aggregrated_db_payload) 
 
 
        print(f"{chat_request.method}") 
        agent = AgentRouting() 
        services_to_call = agent.select_service(user_query=chat_request.user_query, method=chat_request.method) 
 
 
        print(f"Triggering Microservices to:{services_to_call}") 
        service_params = { 
            "user_query":chat_request.user_query, 
        } 
        if 'None' not in services_to_call: 
            subtask_id = await trigger_selected_microservices(services = services_to_call,service_params=service_params) 
 
            print(f"Subtask Id's : {subtask_id}") 
        else: 
            subtask_id = {} 
            print(f"Subtask Id's : {subtask_id}") 
 
        return TaskResponse(task_id=parent_task_id,chat_id=aggregrated_db_payload['chat_id'],session_id = chat_request.session_id , subtask_response = subtask_id) 
 
    except (httpx.RequestError, httpx.HTTPStatusError) as e: 
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=f"Error connecting to agents services : {e}") from e 
     
    except KeyError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Missing required fields : {e}") from e 
     
    except ValueError as e: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid Value : {e}") from e 
     
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Internal Server Error occured : {e}") from e 
         
if __name__ =="__main__": 
    uvicorn.run(app,host = "127.0.0.1",port = 8001) 
 
# uvicorn main:app --host localhost --port 8001