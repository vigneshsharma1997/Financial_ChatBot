from fastapi import FastAPI, HTTPException , Request , status # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from app.app import process_document_search,process_document_upload
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

class DocumentPayload(BaseModel):
    session_id : str
    file_name:str

@app.post("/document_upload")
async def document_upload(request:DocumentPayload):
    try:

        # payload = await request.json()
        # set_session_id(payload["session_id"])
        req = request.dict()
        print("Recieved request for document upload.")
        print("Processing document upload with payload : %s",req)
        result = process_document_upload(req)
        if 'error' in result.keys():
            print("Error processing request: %s",str(result['error']))
            raise HTTPException(status_code = 400 , detail=INVALID_JSON_ERROR)
        else:
            print("Document upload process successfully.")
    except Exception as e:
        raise HTTPException(status_code = 400,detail = INVALID_JSON_ERROR)
    
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)

# uvicorn main:app --host localhost --port 8000

# curl -X POST http://127.0.0.1:8000/document_upload \
#      -H "Content-Type: application/json" \
#      -d '{"session_id": "1234", "file_name": "kpi_data_report.pdf"}'
