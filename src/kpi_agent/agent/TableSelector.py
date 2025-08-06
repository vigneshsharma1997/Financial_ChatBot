
"""
This module contains the TableSelector class, which selects the most relevant
SQL tables based on a user prompt and table descriptions using an LLM.
"""

import json
import re
import time
from typing import Any, Dict, Optional

import pandas as pd
# from utlis.config import DocIngestConfig
from common.llm_connection import llm_model
# Local Imports
# from utils.logger import get_logger, log_performance

# Set Logger
# logger = get_logger(__name__)


class TableSelector(object):
    """
    A class to select the most relevant SQL tables
    based on a user prompt and table descriptions using an LLM.
    """

    def __init__(
        self,
        # config_dict: DocIngestConfig,
        table_descriptions_file,
        instruction_file: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initializes the TableSelector with necessary parameters.

        Args:
            config_dict (DocIngestConfig): The GPT credentials.
            table_descriptions_file (str): Path to CSV file containing table descriptions.
            instruction_file (str): Path to the file containing the LLM instructions.
            max_retries (int, optional): Maximum number of retries for API calls. Defaults to 3.
            retry_delay (float, optional): Delay between retries in seconds. Defaults to 1.0.
        """
        # self.config_dict = config_dict
        self.table_descriptions_file = table_descriptions_file
        self.instruction_file = instruction_file
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.llm_client = llm_model()
        # self.logger = get_logger(__name__)

        self.instructions = self._load_instructions()
        self.table_descriptions = self._load_table_descriptions()

    def _load_instructions(self) -> str:
        """
        Load the instruction text from the specified file.

        Returns:
            str: The instructions loaded from the file.

        Raises:
            FileNotFoundError: If the instructions file is not found.
        """
        try:
            with open(self.instruction_file, "r", encoding="utf-8") as file:
                instructions = file.read()
            print(
                "Instructions loaded successfully from %s", self.instruction_file
            )
            return instructions
        except FileNotFoundError:
            print("Instruction file not found at %s", self.instruction_file)
            raise

    def _load_table_descriptions(self) -> Dict[str, str]:
        """
        Load table descriptions from the CSV file.

        Returns:
            Dict[str, str]: A dictionary with table names as keys and descriptions as values.

        Raises:
            FileNotFoundError: If the table descriptions file is not found.
        """
        try:
            df = pd.read_csv(self.table_descriptions_file)
            table_descriptions = dict(zip(df["TableName"], df["Description"]))
            print(
                "Table description loaded successfully from %s", self.table_descriptions_file
            )
            return table_descriptions
        except FileNotFoundError:
            print(
                "Table descriptions file not found at %s", self.table_descriptions_file
            )
            raise
        except pd.errors.ParserError as e:
            print("Error parsing table descriptions CSV: %s", str(e))
            raise
        except Exception as e:
            print("Error loading table descriptions: %s", str(e))
            raise
    
    @staticmethod
    def _extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
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
                print("Successfully extracted JSON from API response.")
                return json_obj
            print("No valid JSON structure found in the response.")
            return None
        except json.JSONDecodeError as e:
            print("Failed to parse extracted JSON: %s", str(e))
            return None

    # @log_performance
    def select_relevant_tables(self, user_prompt: str) -> tuple[bool, Optional[list[str]]]:
        """
        Select the most relevant tables based on the user prompt using the OpenAI API.

        Args:
            user_prompt (str): The user's query or prompt.

        Returns:
            Optional[list[str]]: List of relevant table names, or None if selection fails.
        """
        prompt = (
            f"{self.instructions}\n\nUser Prompt: {user_prompt}\n\nTable Descriptions:\n"
        )
        for table, description in self.table_descriptions.items():
            prompt += f"{table}: {description}\n"

        for attempt in range(self.max_retries):
            try:
                print("Sending API requests, attempt %d", attempt + 1)
                # response = self.llm_client.send_sync_request(prompt)
                response = self.llm_client.invoke(prompt)
                response_text = response.content.strip()
                print("response_text: ",response_text)
                extracted_json = TableSelector._extract_json_from_response(response_text)
                if extracted_json and "relevant_tables" in extracted_json:
                    relevant_tables = extracted_json["relevant_tables"]
                    if isinstance(relevant_tables, list) and len(relevant_tables) > 0:
                        print(
                            f"Successfully extracted relevant table(s) from API response: {relevant_tables}"
                        )
                        return True, relevant_tables
                    print("No relevant tables found for the given user prompt")
                    return False, None
                self.logger.warning(
                    "Attempt %d: Failed to extract valid JSON or 'relevant_tables' key from API response",
                    attempt + 1,
                )
            except (KeyError, json.JSONDecodeError) as e:
                print(
                    "Attempt %d: Error during API call or JSON extraction: %s",
                    attempt + 1,
                    str(e),
                )
            if attempt < self.max_retries - 1:
                print("Retrying in %f seconds...", self.retry_delay)
                time.sleep(self.retry_delay)
        print("All attempts to analyze columns failed")
        return False, None

    def run(self, user_prompt: str) -> Dict[str, Any]:
        """
        Run the table selection process based on the user prompt.

        Args:
            user_prompt (str): The user's query or prompt.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'relevant_tables_found': A boolean indicating if any relevant tables were found.
                - 'relevant_tables': A list of relevant table names (or None if no tables were found).
                - 'message': A string providing additional context about the result.
        """
        print("Starting table selection process...")
        tables_found, relevant_tables = self.select_relevant_tables(user_prompt)

        result = {
            "relevant_tables_found": tables_found,
            "relevant_tables": relevant_tables,
            "message": "",
        }

        if tables_found:
            result["message"] = f"Found {len(relevant_tables)} relevant table(s) for the given prompt."
            print("Table selection process completed successfully")
        else:
            if relevant_tables is None:
                result["message"] = "An error occurred during the table selection process."
                print("Table selection process failed.")
            else:
                result["message"] = (
                    "No relevant tables found for the given prompt. "
                    "The query may not be related to the available data."
                )
                print("Table selection process completed. No relevant tables found.")

        return result
