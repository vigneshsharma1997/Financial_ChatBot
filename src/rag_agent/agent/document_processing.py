import json
from collections import Counter
from pathlib import Path
from utils.config import document_pipeline_config,processor_config
from dotenv import load_dotenv
load_dotenv()
from common.llm_connection import llm_module
class DocumentProcessor(object):
    """
    A class for processing extracted files. This class performs content extraction and cleanup.
    """
    def __init__(self,input_files:list,output_dir:str):
        print("Inside Initialization")
        self.input_files= input_files
        self.files = list(
            filter(
                lambda fn:Path(fn).suffix == '.json',input_files
            )
        )

        self.n_files = len(self.files)
        self.output_dir = Path(output_dir)
        self.processor_config =processor_config
        self.chunk_method = self.processor_config['chunk_method']
        self.current_block = {'content':"","page_number":[],"type":[]}
        self.counts = {'nltk':0,'llm':0,'table':0,'image':0}
        self.llm = None
        if (len(self.processor_config['clean_llm'])>0 | len(self.processor_config['type_image'])>0):
            self.llm = llm_module()
        print(f"Document Processor initialized with {self.n_files} files.")
    
    def _refresh_blocks(self):
        """
        Resets the current processing block to its initial state.
        This method clears the content, Page Number and Type of the current block, essentially preparing it for new data or content to be processed.
        """
        self.current_block = {"content":"","page_number":[],"type":[]}

    def _check_item_categories(self,item)->dict[str,bool]:
        """
        Categorizes the given based on its type and predefined categories.
        This method checks the item's type against various categories defined in the processor config.
        It returns a dictionary indicating whether the item belongs to each of the following categories.
        - ** nltk ** : If the item type matches any options in the 'clean_nltk' config list.
        - ** llm ** : If the item type matches any options in the 'clean_llm' config list.
        - ** table ** : If the item type matches any options in the 'type_table' config list.
        - ** image ** : If the item type matches any options in the 'type_image' config list.
        """
        item_type = item['type'].lower()
        item_cats  = {
            'nltk': any(option in item_type for option in self.processor_config['clean_nltk']),
            'llm': any(option in item_type for option in self.processor_config['clean_llm']),
            'table': any(option in item_type for option in self.processor_config['type_table']),
            'image': any(option in item_type for option in self.processor_config['type_image'])
        }
        return item_cats

    def process_items(self,item:dict):
        """
        
        """
        content = ""
        # item_cats = self._check_item_categories(item)  #Not Required as of now 
        if len(content) == 0:
            # print(item['content'])
            content = item['content']
        return content

    def _check_switch_blocks(self,item:dict)->bool:
        """
            Determine whether it's time to a new block of content based on the current chunking method.
            This method evaluates the current content (item) and checks whether the block should switch according to the defined 'chunk_method'. It uses different criteria depending on whether the chunking method is 'use_existing' , 'by_type' or 'by_page' .
            Args :
                item(dict): A dictionary representing a single item of content expected to contain keys like type,content,page_number.
            Returns:
                bool: True if the current block should switch; False otherwise.
        """
        block_has_len = len(self.current_block['page_number']) > 0

        switch_due_to_content_length = len(self.current_block['content']) > 8000
        if self.chunk_method == 'use_existing':
            return True
        switch_due_to_title = self.chunk_method == 'by_type' and item['type'] == 'page_text' and block_has_len
        
        switch_due_to_page = self.chunk_method == 'by_page' and block_has_len
        if switch_due_to_page:
            item_page = item.get('page_number',None)
            if item_page is not None:
                page_numbers = [elem.get('page_number') for elem in self.current_block['page_number']]
                page_numbers = list(filter(lambda s: s is not None,page_numbers))
                if item_page not in page_numbers:
                    switch_due_to_page = True
                else:
                    switch_due_to_page = False
            else:
                switch_due_to_page = False
        # print(f"Switch due to content : {switch_due_to_content_length} , title : {switch_due_to_title} , page : {switch_due_to_page}")
        return switch_due_to_content_length,switch_due_to_title,switch_due_to_page


    def _check_relevant_items(self,item)->bool:
        """
        Checks if the given item is relevant based on the predefined matching criteria.
        This methods evaluate if the item type matches any of the criteria defined in the processor configuration.
        It checks for two types of matches:
        - ** Lowercase match** : If the item's type (converetd to lowercase) is present in the type 'type_lowercase_match' config list.
        - ** Word within match ** : If any word in the type word withinf config list is a substring of item's type.

        """
        
        lowercase_match = item['type'].lower() in self.processor_config['type_lowercase_match']
        word_within_match = any(item_type in item['type'].lower() for item_type in self.processor_config['type_word_within'])
        # print(f"Check Relvant Items lowercase Match:{lowercase_match} ,word within match: {word_within_match} ")
        return lowercase_match | word_within_match


    def process_contents(self,data:dict)->list:
        """
            Processes the extracted document content into structured blocks.
            Chunking determined by self.chunk_method , either 'using _existing (default) , 'by_page' or 'by_title'
            Args : 
                data : dict from JSON object
            Returns:
                list : A list of structured content blocks , each containing text and metadata.
        """
        final_content = []
        self._refresh_blocks()
        print(Counter(item['type'] for item in data))
        for item in data:
            content = None
            # print("Item : ",item)
            # Determine if it's time for next block
            if self._check_switch_blocks(item):
                final_content.append(self.current_block)
                self._refresh_blocks()
            # Process Item:
            try:
                if self._check_relevant_items(item):
                    # print("Inside Check relevant items")
                    content = self.process_items(item)
                else:
                    print(f"Item of type {item['type']} not processed.")
                    content = None
                if content is not None:
                    self.current_block['content'] += f"{content}"
                    self.current_block['page_number'].append(item.get('page_number',{}))
                    self.current_block['type'].append(item.get('type',""))
            
            except Exception as e:
                # print(f"Error processing items: {item.get('page_number',item)}")
                print(f"Error message {e}")
                continue
        if self.current_block['content']:
            final_content.append(self.current_block)
        # print(f"Final Content: {final_content}")
        print("Processed content into strucured blocks")
        print(f"Process usage counts: {self.counts}")
        return final_content


    def run(self)->list[Path]:
        print("Inside Run")
        processed_json_data = []
        failed_files= []
        for json_file in self.files:
            try:
                # json_data = json.loads(json_file)
                
                with open(json_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                processed_content = self.process_contents(json_data)

                json_elements = json.dumps(processed_content,indent=2)
                
                output_file = self.output_dir/f"{json_file.stem}.json" 
                output_file.parent.mkdir(parents=True,exist_ok=True)
                try:
                    with open(output_file,'w',encoding='utf-8') as f:
                        json.dump(processed_content,f,indent=2,ensure_ascii=False)
                    processed_json_data.append(output_file)
                except Exception as e:
                    print(f"Failed to write JSON to {output_file}: {e}")
                
            except Exception as e:
                failed_files.append(json_file)
                print(f'File {json_file} failed with exception {e}')
        return processed_json_data
    
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