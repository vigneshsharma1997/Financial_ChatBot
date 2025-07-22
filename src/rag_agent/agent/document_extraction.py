import json
from pathlib import Path
import unstructured.partition
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import dict_to_elements , elements_to_json

from utils.config import allowed_extentions
class DocumentExtractor(object):
    """
        A class for extracting files in Azure using the Unstrcutured API.
    """
    def __init__(self,input_files:list[Path],output_dir:str):
        self.input_files = input_files
        self.files = list(
            filter(
                lambda fn : Path(fn.filename).suffix in allowed_extentions,input_files
            )
        )
        self.n_files = len(self.files)
        self.extracted_files = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Document_Extractor initialized with {self.n_files} files.")

    def partition_file(self,filename):
        elements = partition_pdf(filename)
        ele_dict = [el.to_dict() for el in elements]
        output_json = json.dumps(ele_dict, indent=2)

        # Save to JSON
        output_file = self.output_dir / f"{filename.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output_json)

        print(f"Saved extracted content to: {output_file}")
        return output_file
    
    def run(self) -> list[Path]:
        """
        Process a list of files , extracting content
        Args :
            None
        Return :
             list of dict : A list of dictionaries containing metadata and content for each processed file.
        """
        print(f"Extracting {self.n_files} files...")
        for file in self.files:
            result = self.partition_file(file)
            self.extracted_files.append(result)
            print(f"Extraction complete.")
            return self.extracted_files
        

def run_data_extraction(input_files : list[str],extraction_dir:str) -> list:
    """
        Main Function to run the document data extraction process.
        Args:
            input_files(list[str]) : List of files to process.
            extraction_dir(str): Directory to save extracted data.
        Returns :
            List of json files where extractions are loaded.
        Raises : 
            Exception : If there is an error during the data extraction process.
    """    
    print(f"Starting document data extraction process for. {len(input_files)} files.")
    doc_extractor = DocumentExtractor(input_files,extraction_dir)
    json_files = doc_extractor.run()
    return json_files