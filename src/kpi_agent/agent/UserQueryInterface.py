"""
This module contains the UserQueryInterface class, which handles user queries
by merging the current query with previous chat history for better context.
"""

# General
import os
from pathlib import Path
from typing import Dict, Union

# Third Party Imports
import pandas as pd
from utils.config import AGENT_NAME#, set_default_config
from common.llm_connection import llm_module
# Local Imports
# from core.logger import get_logger, log_performance

# Set Logger
# logger = get_logger(__name__)
path = os.path.dirname(__file__)

class UserQueryInterface(object):
    """
    A class to handle user queries by finding and merging previous chat history
    to provide better context for LLM-based query processing.
    """

    def __init__(
        self,
        session_id: str,
        user_query: str,
        prompt_path: str
    ):
        """
        Initializes the UserQueryInterface with necessary parameters.

        Args:
            session_id (str): Unique session identification number for each session.
            user_query (str): User's input query.
            prompt_path (str): Path to the text file containing the prompt template.
        """
        self.user_query = user_query
        self.session_id = session_id
        self.logger = get_logger(__name__)  
        self.prompt_path = Path(prompt_path)
        self.prompt_template = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """
        Load the system prompt template from specified file.
        
        Returns:
            str: Content of the system prompt template
            
        Raises:
            FileNotFoundError: If the system prompt file doesn't exist
            IOError: If there are issues reading the system prompt file    
        """    
        try:
            return self.prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"System prompt file not found at: {self.prompt_path}") from e
        except IOError as e:
            raise IOError(f"Error reading system prompt file: {e}") from e

    @staticmethod
    def format_chat_history(df: pd.DataFrame) -> str:
        """ 
        Format the conversation history data frame into a readable text format.
        
        Args:
            df: DataFrame with columns prompt_text and response_text.
            
        Returns:
            str: Formatted conversation history as a string    
        """
        try:
            answers = df['response_text'].fillna("[No answer provided]")
            
            indexes = (df.reset_index(drop=True).index + 1).astype(str)
            
            qa_pairs = "#" + indexes + "\nQuestion: " + df["prompt_text"].astype(str) + "\nAnswer: " + answers.astype(str)
            return '\n\n'.join(qa_pairs.tolist())    
        except Exception as e:
            logger.info(f"Error during chat history merge: {e}")
            return ""
            
    def get_relevant_context(self, df: pd.DataFrame) -> str:
        """ 
        Extract relevant context from chat history to enrich the current user query.
        
        Args:
            df (pd.DataFrame): DataFrame with columns prompt_text, answer_text, and answer_table

        Returns:
            str: A string with relevant context or empty string if no relevant information exists        
        """
        if df is None or df.empty or not all(col in df.columns for col in ['prompt_text', 'response_text']):
            return "" 
        
        chat_history = UserQueryInterface.format_chat_history(df)

        prompt = self.prompt_template.format(query=self.user_query,
                                             chat_history=chat_history
                                             )
        
        try:
            config_dict = set_default_config()
            llm_client = LLMClient(config_dict)
            response = llm_client.send_sync_request(prompt)["choices"][0]["message"]["content"]  
            logger.info(f"Context was extracted from chat history: {response}")
            return response if "NO_RELEVANT_CONTEXT" not in response else "" 
        except Exception as e:
            logger.info(f"Error in context extraction: {e}")
            return ""   
        
    # @log_performance
    def fetch_and_merge_chat(self, chat_history: pd.DataFrame) -> Union[str, Dict[str, str]]:
        """
        Fetches the user's previous chat history from the provided CSV and merges it
        with the current query for better context.

        Args:
            chat_history (pd.DataFrame): A DataFrame containing previous chat prompts.

        Returns:
            Union[str, Dict[str, str]: The merged query with previous chat context or just the current query
                if no previous chats are found.
                Sample response dictionary is returned if the function fails.
        """
        try:
  
            if not chat_history.empty and 'prompt_text' in chat_history.columns and not chat_history['prompt_text'].dropna().empty:
                chat_context = self.get_relevant_context(chat_history)
            else:
                chat_context = ""
            merged_query = '\n\n'.join([self.user_query, chat_context])
            self.logger.info(f"Merged query: {merged_query}")
            self.logger.info(
                "Merged prompt successfully created for session_id: %s",
                self.session_id,
            )

            return merged_query

        except Exception as e:
            self.logger.error("Error processing the user chat history %s", e)
            return {
                "CanIAnswerThePrompt": False,
                "agent_name": AGENT_NAME,
                "answer_text": f"<p>Error processing from User Query Interface {e} </p>",
                "response_metadata": {"answer_img": [],
                                      "answer_table": [],
                                      "explanation": ""
                                    }
            }