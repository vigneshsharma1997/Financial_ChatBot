import uuid 
import time 
 
insert_chat_query = """ 
INSERT INTO session_chat_sql (session_id, chat_id, source_agent, prompt_text, question_title, created_at) 
VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP()) 
""" 
 
def generate_task_id() ->str: 
    task_id = str(uuid.uuid4()) 
    return task_id 
 
def generate_global_chat_id(): 
    chat_id = str(int(time.time()*1000)) 
    return chat_id 