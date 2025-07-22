import json
from collections import Counter
from pathlib import Path
from utils.config import document_pipeline_config
from dotenv import load_dotenv
load_dotenv()

class DocumentProcessor(object):
    pass

def run_data_processing(input_files:list,process_dir):
    """
        Main function to run document data extraction process.
        Args:
            input_files : list() List of Blob files.
            process_dir : Directory to save processed data.
        Return : List of processed json files.
        Raises Exception: If there are any error during the pdf data extraction process.
     """
    print(f"Running processing for {len(input_files)} files.")
    doc_processor = DocumentProcessor(input_files,process_dir)
    processed_json_files = doc_processor.run()
    if len(input_files) == len(processed_json_files):
        print("All JSON files have been saved successfully.")
    else:
        print("Mismatch in number of files in path.")
    return processed_json_files