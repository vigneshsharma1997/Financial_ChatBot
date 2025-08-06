import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd
from utils.config import set_default_config
from common.llm_connection import llm_module
# from utils.logger import get_logger

# Set Logger
# logger = get_logger(__name__)

class TaskEvaluator(object):
    """
    A class that evaluates whether a user's query can be answered using available data sources
    and determines which agent should handle the query.
    """
    def __init__(self, system_prompt_path: Union[str, Path]) -> None:
        """
        Initialize the TaskDivider with a system prompt file path.
        
        Args:
            system_prompt_path: Path to the system prompt template file
            
        Returns:
            None.
        """
        self.system_prompt_path = Path(system_prompt_path)
        self.config  = set_default_config()
        self.client = LLMClient(self.config)
        self.system_prompt = self._load_system_prompt()
        self.logger = get_logger(__name__)
        
        self.logger.info("TaskEvaluator has been initialized")
        
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
            return self.system_prompt_path.read_text(encoding="utf-8")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"System prompt file not found at: {self.system_prompt_path}") from e
        except IOError as e:
            raise IOError(f"Error reading system prompt file: {e}") from e
        
    def _format_prompt(self, user_prompt: str, data_sources: Dict[str, str],
                       prompt_history: Optional[pd.DataFrame] = None) -> str:
        """
        Combine the system prompt template with the user's input prompt.
        
        Args:
            user_prompt: The user's query to evaluate
            data_sources: Dictionary mapping data source descriptions to their file paths.
            prompt_history: DataFrame containing previous prompts with 'prompt_text' column
                
        Returns:
            str: Formatted prompt ready for LLM processing, combining the system prompt
            template with the user's query, available data sources and chat history.
        """            
        
        previous_prompts = []
        if prompt_history is not None:
            if not prompt_history.empty and 'prompt_text' in prompt_history.columns:
                previous_prompts = prompt_history['prompt_text'].dropna().tolist()
                
        return self.system_prompt.format(user_prompt=user_prompt,
                                         data_sources=list(data_sources.keys()),
                                         prompt_history=previous_prompts)
    @staticmethod
    def _extract_json_from_response(
        response_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a valid JSON object from the API response text.

        Args:
            response_text (str): The full text response from the API.

        Returns:
            Optional[Dict[str, Any]]: Extracted JSON object or None if no valid JSON found.
        """
        try:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                json_obj = json.loads(json_str)
                return json_obj
            else:
                return None

        except json.JSONDecodeError:
            return None    
        
    def evaluate_task(self, user_prompt: str, data_sources: Dict[str, str],
                      prompt_history: Optional[pd.DataFrame] = None) -> Dict[str, bool]:
        """
        Evaluates whether the user's query can be answered with the available data sources.
        
        Args:
            user_prompt: The user's query to evaluate
            data_sources: Dictionary mapping data source descriptions to their file paths
                
        Returns:
            Dict[str, bool]: A dictionary with a single key "feasible" mapping to a boolean
            indicating whether the task can be completed with the available data sources.
            Returns {"feasible": False} for any error condition or if no data sources are available.
        """ 
        result = {"feasible": False}
        
        if data_sources:       
            try:
                self.logger.info(f"Data Sources provided to the TaskEvaluator: {data_sources}")
                formatted_prompt = self._format_prompt(user_prompt, data_sources, prompt_history)
                response = self.client.send_sync_request(formatted_prompt)
                llm_response = response["choices"][0]["message"]["content"]
                parsed_result = TaskEvaluator._extract_json_from_response(llm_response)

                self.logger.info(f"TaskEvaluator has responded with: {parsed_result}")
                
                if "feasible" in parsed_result:
                    result = parsed_result
                
            except Exception as e:
                self.logger.info(f"Error in TaskEvaluator: {e}")
            
        return result    
        

    def select_agent(self, user_prompt: str, data_sources: Dict[str, str],
                     prompt_history: Optional[pd.DataFrame] = None) -> Dict[str, bool]:
        """ 
        Determine which agent should handle the user's query.
        
        Args:
            user_prompt: The current user query 
            data_sources: Dictionary of data source descriptions 
            prompt_history: DataFrame containing previous prompts with 'prompt_text' column 
            
        Returns:
            Dict[str, bool]: Dict indicating whether plotting and/or data analytics agents are needed.    
        """        

        try:
            self.logger.info(f"Data Sources provided to the AgentSelector: {data_sources}")
            formatted_prompt = self._format_prompt(user_prompt, data_sources, prompt_history)
            self.logger.info(f"Prompt created")
            response = self.client.send_sync_request(formatted_prompt)
            llm_response = response["choices"][0]["message"]["content"]
            result = TaskEvaluator._extract_json_from_response(llm_response)

            self.logger.info(f"AgentSelector has responded with: {result}")
            
            if "needs_plotting" not in result or "needs_analytics" not in result:
                return {"needs_plotting": True, "needs_analytics": True}

            return result
             
        except Exception as e:
            self.logger.info(f"Error in AgentSelector: {e}")
            return {"needs_plotting": True, "needs_analytics": True} 
