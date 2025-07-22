from typing import Any,Dict,List,Optional,Union
import pandas as pd
import json
import os
import pydoc
from dotenv import load_dotenv
import mysql.connector
from common.sql_constants import (GET_SESSION_CHAT_SQL,INSERT_SESSION_ARTIFACTS_TO_DB,INSERT_SESSION_CHAT_TO_ID,UPDATE_DATA_TO_SESSION_CHAT)

class MyDbConnection(object):
    """
        Handles the database connection insert , update , and close operations.
        This class provides methods to connect to the database , insert records , update records,read from the database and close the connection. It uses pyodc for SQL interactions and handles all database transactions.
    """
    def __init__(self):
        self.host = os.getenv("db_hostname")
        self.port = os.getenv("db_port")
        self.username = os.getenv("db_username")
        self.password = os.getenv("password")
        self.database = os.getenv("db")
        self.conn = None
        self.cursor = None
    
    def connect(self):
        connection = mysql.connector.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            database = self.database
        )
        if connection.is_connected():
            print("Connected to MySql Server.")
        self.conn = connection
        self.cursor = connection.cursor()
    
    def read_session_chat_sql(self,session_id:str) -> List[Dict[str,Any]]:
        """
            Fetches rows based on session_id and/or Chat_id.
            Args : 
                session_id (str) : The session id to search for.
            Returns :
                List : A list of dictionaries containing the query results, or an empty list if no results are found.
            Raise :
                Exception : If an error occurs during the database query, an exception is raised with error message. 
        """     
        try :
            print("Fetching rows for session id:%s",session_id)
            self.cursor.execute(GET_SESSION_CHAT_SQL,session_id)
            rows = self.cursor.fetchall()
            result = [
                {desc[0]:row[idx] for idx,desc in enumerate(self.cursor.description)}
                for row in rows
            ]
            self.print("Successfully fetched rows for session_id %s",session_id)
            return result
        except Exception as e:
            raise RuntimeError("Unexpected error while reading rows for session id") from e

def read_from_session_chat(payload:Dict[str,Any]) -> Optional[pd.DataFrame]:
    """
        Reads a row from the databases based on session_id and/or chat_id and returns as a DataFrame.
        Returns an empty DataFrame if no results are found.
        Args : 
            payload(dict) : A dictionary containing the session_id and/or Chat_id.
        Returns:
            pd.DataFrame : A DataFrame containing the query results or an empty DataFrame if no results.
    """

    try:
        with MyDbConnection() as db:
            session_id = payload.get('session_id')
            result = db.read_session_chat_sql(session_id)
        if result:
            return pd.DataFrame(result)
        else:
            return pd.DataFrame()
    except Exception as e:
        print("Error in read session Id : %s",e)
        return pd.DataFrame()
    
