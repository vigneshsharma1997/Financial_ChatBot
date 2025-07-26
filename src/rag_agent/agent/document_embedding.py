from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import os
import uuid

def embed_documents_chunks(data_input:list[Path],output_dir:str)->list:
    """
        Processes a list of documents, extracts text, generates embeddings in batches, and returns a DataFrame with embedding added.
        Args : 
            data_input (list) : A list of files containing the documents to process.
            output_dir (str) : Directory to output updated Chunks.
        Returns :
            str : Datetime of processed batch for file identification. 
    """
    created_at = datetime.now()
    batch_size = int(os.getenv("BATCH_SIZE"))
    print("Starting document embedding for %d files.",len(data_input))
    print("Starting document embedding for %d files.",len(batch_size))
    batch = []
    output_files = []
    