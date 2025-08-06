import os 
from dotenv import load_dotenv 
load_dotenv() 
import mysql.connector 
from utils.config import insert_chat_query 
 
 
class MySqlConnection(object): 
    def __init__(self): 
        self.host = os.getenv("db_host_name") 
        self.port = os.getenv("db_port") 
        self.username = os.getenv("db_username") 
        self.password = os.getenv("password") 
        self.database = os.getenv("db") 
        self.conn = None 
        self.cursor = None 
        print("Constructor initialized.")
 
    def connect(self): 
        print("Inside connect.") 
        connection = mysql.connector.connect( 
            host = self.host, 
            port = self.port, 
            user = self.username, 
            password = self.password, 
            database= self.database 
        ) 
        if connection.is_connected(): 
            print("Connected to MySQL Server.") 
        self.conn = connection 
        self.cursor = connection.cursor()    
     
    def insert(self,session_id,chat_id,source_agent,user_query): 
        try: 
            print("inside Insert().") 
            self.connect() 
            self.cursor.execute(insert_chat_query,(session_id,chat_id,source_agent,user_query)) 
            self.conn.commit() 
            print("Query Executed successfully.") 
        except Exception as e: 
            print(f"Error in inserting to database due to {e}") 
 
def insert_session_id_chat_id_to_db(payload): 
    try : 
        db = MySqlConnection()  
        print("Inside Insert Query") 
        db.insert(payload["session_id"],payload["chat_id"],payload["source_agent"],payload["user_query"]) 
        return True 
    except Exception as e: 
        return False       
 
# payload= { 
#     "session_id": "abcd", 
#     "chat_id" : "def", 
#     "user_query": "What is my VOH for NUSA factory", 
#     "source_agent": "combined_agents", 
#     "question_title": "VOH for NUSA factory"   # <-- Add this 
# } 
 
     
# insert_session_id_chat_id_to_db(payload) 
