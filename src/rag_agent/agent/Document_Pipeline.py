import json
from pathlib import Path
from typing import Optional
from utils.config import folders
from agent.document_extraction import run_data_extraction
from agent.document_processing import run_data_processing

class DocumentPipeline:
    def __init__(self):
        self.folders = folders.copy()
    
    # def get_folder_files(self,folder)->list[Path]:
    #     folder_path = Path(self.folders.get(folder, ""))
    #     if not folder_path.exists() or not folder_path.is_dir():
    #         return []
    #     return [f for f in folder_path.iterdir() if f.is_file()]
    def get_folder_files(self, folder_path: str) -> list[Path]:
        folder_path = Path(folder_path)
        if not folder_path.exists() or not folder_path.is_dir():
            return []
        return [f for f in folder_path.iterdir() if f.is_file()]

    def run(self,extract_files:Optional[bool],process_files:Optional[bool],embed_files:Optional[bool],upsert_files:Optional[bool]):
        """
            Runs the document processing piepline using defined configuration.

            This methods orchestrates the execution of the document pipeline by sequentially runninfg different stages (extraction,processing,embedding and upserting ) based on the given flags. It fetches files from specific folders, processes them according to the config and perform necassary actions for each stage.

            Args:
                extract_files(Optional[bool],default=True):Flag indicatinf whether to run the data extraction process.
                process_files(Optional[bool],default=True):Flag indicatinf whether to run the data processing process.
                embedd_files(Optional[bool],default=True):Flag indicatinf whether to run the data embedding stage.
                upsert_files(Optional[bool],default=True):Flag indicatinf whether to upsert operations into vector databse.
            Returns:
                None this method does not return any value. It executes each stage of the pipeline as configured.
        """
        fns_input = self.get_folder_files(self.folders['input'])
        print("Input Folder Name:",fns_input)
        if extract_files:
            print(f"{len(fns_input)} files are ready for extraction.")
            fns_extracted = run_data_extraction(fns_input,self.folders['extracted'])
        if process_files:
            if not extract_files:
                fns_extracted = self.get_folder_files(self.folders['extracted'])
            print(f"{len(fns_extracted)} files are ready for processing.")
            fns_processed = run_data_processing(fns_extracted,self.folders['processed'])
        # if embed_files:
        #     if not process_files:
        #         fns_processed = self.get_folder_files(self.folders['processed'])
        #     print(f"{len(fns_processed)} files are ready for embeddings")
            

