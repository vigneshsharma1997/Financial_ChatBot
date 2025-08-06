from fastapi import FastAPI, HTTPException , Request , status # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from app.app import process_main
INVALID_JSON_ERROR = "Invalid JSON input"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = False,
    allow_methods=["GET","POST","OPTIONS"],
    allow_headers = ["*"]
)

class QueryPayload(BaseModel):
    session_id : str
    user_query : str
    chat_id : str

@app.post("/agent/kpi_insight/")
async def document_upload(request:QueryPayload):
    try:
        task = process_main(
            request.session_id,
            request.user_query,
            request.chat_id
        )
        return {"task_id":task,"status":"Task has been started"}
    except Exception as e:
        raise HTTPException(status_code = 500,detail = str(e))
    
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8001)

# uvicorn main:app --host localhost --port 8001