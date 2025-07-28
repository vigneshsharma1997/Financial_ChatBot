import json
import os
from typing import Any,Dict
from dotenv import load_dotenv
from utils.config import AGENT_NAME
from agent.chat_history import answer_from_existing_data
from agent.Document_Pipeline import DocumentPipeline
from utils.config import document_pipeline_config
load_dotenv()

def process_document_upload(payload:Dict[str,Any]) -> Dict[str,Any]:
    try :
        pipeline = DocumentPipeline()
        pipeline.run(
            extract_files = document_pipeline_config['extracting_on'],
            process_files = document_pipeline_config['processing_on'],
            embed_files = document_pipeline_config['embedding_on'],
            upsert_files = document_pipeline_config['upserting_on']
        )
        return payload
    except Exception as e:
        print("Error in process_document_upload: %s",e)
        return {"error":"Failed to process document upload."}



def process_document_search(payload:Dict[str,Any])->Dict[str,Any]:
    """
        Processes a document search by checking if there is an exisiting answer,
        and if not retrieving relevant document and performing a Q&A task on them.
        Args:
            payload(Dict[str,Any]) : A dictionary containing the user query and session data.
        Returns:
            Dict[str,Any] : A dictionary containing the response data with answer and metadata or any message.
    """
    response = {}

    try:
        payload['source_agent'] = 'rag-agent'
        existing_chat_data = answer_from_existing_data(payload)
        if not existing_chat_data['can_answer']:
            response = handle_new_query(payload,existing_chat_data)
        else:
            response = handle_existing_response(payload,existing_chat_data)
    except Exception as e:
        response = build_error_response(f"Error processing : {str(e)}")

def handle_existing_response(payload:Dict[str,Any],exisiting_chat_data:Dict[str,Any])->Dict[str,Any]:
    pass

def handle_new_query(payload:Dict[str,Any],exisiting_chat_data:Dict[str,Any])->Dict[str,Any]:
    pass

def build_error_response(error_message:str) -> Dict[str,Any]:
    return {
        "CanIAnswerPrompt":"False",
        "agent_name":AGENT_NAME,
        "answer_text":f"<p>{error_message}</p>",
        "response_metadata":{"metadata":[],"answer_img":[]}
    }