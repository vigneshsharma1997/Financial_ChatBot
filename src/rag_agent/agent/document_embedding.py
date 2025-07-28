from datetime import datetime
from pathlib import Path
from typing import Optional
import json
import os
import uuid
from nomic import embed
from dotenv import load_dotenv
load_dotenv()
# import os
nomic_api_key = os.getenv("NOMIC_API_KEY")

def generate_batch_embeddings(batch:list[str]) -> list:
    try:
        response = embed.text(
            texts=batch,
            model='nomic-embed-text-v1',
            task_type='embedding',
        )
        embeddings = response['embeddings']
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return []

def embed_batch(batch:list[dict]) ->dict:
    batch_texts = list(map(lambda x: x['document_text'],batch))
    try:
        print("Batch Text: ",batch_texts)
        batch_embeddings = generate_batch_embeddings(batch_texts)
    except Exception as e:
        print(f"Failed to embed batch: {e}")
    return [
        chunk.update({
            "embedding":emb
        }) for chunk,emb in zip(batch,batch_embeddings)
    ]

def generate_hybrid_unique_id(document_name:str,document_chunk:str) ->str:
    uuid_part = str(uuid.uuid4())
    unique_doc_id = f"{document_name}_{document_chunk}_{uuid_part}"
    # print(f"Generated UUID: {unique_doc_id}")
    return unique_doc_id

def format_chunk(chunk:dict,fn_str:str,fn_uri:str,doc_id:int,chunk_id:int) ->dict:
    # print(chunk.keys())
    # page_numbers = [
    #     item['page'] for item in chunk if 'page' in item.keys()
    # ]
    page_numbers = chunk.get("page", None)
    if page_numbers ==0:
        page_numbers = 1
    page_numbers = [page_numbers]    
    chunk_prepared = {
        "document_id":doc_id,
        "document_name": f"{Path(fn_str).stem}",
        "document_link": f"{fn_uri}",
        "chunk_id": chunk_id,
        "page_start":min(page_numbers),
        "page_end":max(page_numbers),
        "document_text":str(chunk['content']),
        "embedding":None,
        "created_datetime":None,
        "updated_datetime":None,
        "unique_id":None
    }
    chunk_prepared.update({
        "unique_id":generate_hybrid_unique_id(
            chunk_prepared['document_name'],
            chunk_prepared['chunk_id']
        )
    })
    return chunk_prepared

def embed_documents_chunks(data_input:list[Path],output_dir:str)->list:
    """
        Processes a list of documents, extracts text, generates embeddings in batches, and returns a DataFrame with embedding added.
        Args : 
            data_input (list) : A list of files containing the documents to process.
            output_dir (str) : Directory to output updated Chunks.
        Returns :
            str : Datetime of processed batch for file identification. 
    """
    created_time = datetime.now()
    batch_size = os.getenv("BATCH_SIZE")
    batch_id=0
    print(f"Starting document embedding for {len(data_input)} files.")
    print(f"Embedding for chunks in batches {len(batch_size)}")
    batch = []
    output_files = []

    for doc_id,fn in enumerate(data_input):
        print(f"==================================")
        print(f"Preparing document: {fn.name}")

        try :
            with open(fn,"r",encoding="utf-8") as f:
                doc_elements = json.load(f)
            # doc_elements = json.loads(fn.name)
        except json.JSONDecodeError as e:
            print(f"Error in decoding json for filename : {fn.name}, error : {e}.")
        
        for chunk_id,data_i in enumerate(doc_elements):
            # print(f"Chunk ID: {chunk_id}, Data: {data_i}")
            batch.append(format_chunk(data_i,fn.name,fn.name,doc_id,chunk_id))
            if isinstance(len(batch),int):
                if len(batch) >= batch_size:
                    try:
                        print("In Batch",batch)
                        batch = embed_batch(
                            batch = batch
                        )
                        
                        # fn_batch = save_batch(
                        #     batch=batch,
                        #     created_time = created_time,
                        #     batch_id = batch_id
                        # )
                        # output_files.append(fn_batch)
                    except Exception as e:
                        print(f"Failed to embed batch : {batch_id}: e")
                    finally:
                        batch=[]
                        batch_id+=1
        # if len(batch)>0:
        #     try:
        #         batch = embed_batch(
        #             batch = batch
        #         )
        #         fn_batch = save_batch(
        #             batch=batch,
        #             created_time = created_time,
        #             batch_id = batch_id
        #         )
        #         output_files.append(fn_batch)
        #     except Exception as e:
        #         print(f"Failed to embed batch : {batch_id}: e")

    print(f"Embeddings complete for {batch_id+1} batches.")
    print(f"Time created : {created_time}")
    # return output_files
    