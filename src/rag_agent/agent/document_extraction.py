import json
from pathlib import Path
# import unstructured.partition
# from unstructured.partition.pdf import partition_pdf
# from unstructured.staging.base import dict_to_elements , elements_to_json
import pdfplumber
import os
import json
from pathlib import Path
import io

# LangChain loaders & utilities
from langchain.document_loaders import (
    # UnstructuredWordDocumentLoader,
    # UnstructuredPowerPointLoader,
    # CSVLoader,
    PyMuPDFLoader,
    # TextLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# OCR
import pytesseract
from PIL import Image

# PDF table extraction
import pdfplumber

# PDF image extraction
import fitz  # PyMuPDF

# HTML parsing for links
from bs4 import BeautifulSoup
import re
from utils.config import allowed_extentions

class DocumentExtractor(object):
    """
        A class for extracting files in Azure using the Unstrcutured API.
    """
    def __init__(self,input_files:list[Path],output_dir:str):
        self.input_files = input_files
        # self.files = list(
        #     filter(
        #         lambda fn : Path(fn.filename).suffix in allowed_extentions,input_files
        #     )
        # )
        print("Input files",input_files)
        self.files = list(
            filter(
                lambda fn: fn.suffix in allowed_extentions,
                input_files
            )
        )
        self.n_files = len(self.files)
        self.extracted_files = []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Document_Extractor initialized with {self.n_files} files.")

    def partition_file(self, filename: Path) -> Path:
        ext = filename.suffix.lower()
        docs = []
        metadata = {"source": str(filename)}
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        try:
            if ext == ".pdf":
                # Extract raw text
                loader = PyMuPDFLoader(str(filename))
                text_docs = loader.load()

                # Chunk text documents
                for doc in text_docs:
                    chunks = text_splitter.split_documents([doc])
                    for idx, chunk in enumerate(chunks):
                        docs.append({
                            "type": "text",
                            "content": chunk.page_content,
                            "page": doc.metadata.get("page"),
                            "chunk_index": idx,
                            "metadata": chunk.metadata,
                            "source": str(filename)
                        })

                # Extract tables using pdfplumber
                with pdfplumber.open(str(filename)) as pdf:
                    for page_num, page in enumerate(pdf.pages, start=1):
                        for table_idx, table in enumerate(page.extract_tables(), start=1):
                            header, *rows = table
                            structured_table = [dict(zip(header, row)) for row in rows if row]
                            docs.append({
                                "type": "table",
                                "content": structured_table,
                                "page": page_num,
                                "chunk_index": table_idx,
                                "metadata": {},
                                "source": str(filename)
                            })

                # Extract hyperlinks from text_docs
                for doc in text_docs:
                    links = re.findall(r'https?://\S+', doc.page_content)
                    if links:
                        docs.append({
                            "type": "hyperlinks",
                            "content": links,
                            "page": doc.metadata.get("page"),
                            "chunk_index": 0,
                            "metadata": {},
                            "source": str(filename)
                        })

                # Optional: Uncomment for image OCR using fitz + pytesseract
                # pdf_doc = fitz.open(str(filename))
                # for p_index, page in enumerate(pdf_doc, start=1):
                #     for img_index, img_info in enumerate(page.get_images(full=True), start=1):
                #         xref = img_info[0]
                #         image_bytes = pdf_doc.extract_image(xref)["image"]
                #         img = Image.open(io.BytesIO(image_bytes))
                #         ocr_text = pytesseract.image_to_string(img)
                #         if ocr_text.strip():
                #             docs.append({
                #                 "type": "image_ocr",
                #                 "content": ocr_text,
                #                 "page": p_index,
                #                 "chunk_index": img_index,
                #                 "metadata": {},
                #                 "source": str(filename)
                #             })

        except Exception as e:
            print(f"Error processing file {filename}: {e}")

        # Write to JSON
        output_file = self.output_dir / f"{filename.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2, ensure_ascii=False)

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
        # print(f"Extracting {self.n_files} files...")
        for file in self.files:
            result = self.partition_file(file)
            self.extracted_files.append(result)
            print(f"Extraction complete.")
        return self.extracted_files
        

def run_data_extraction(input_files : list[Path],extraction_dir:str) -> list:
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

# run_data_extraction()