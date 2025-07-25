AGENT_NAME="rag-agent"
document_pipeline_config = {
    "extracting_on" : True,
    "processing_on" : True,
    "embedding_on" : False,
    "upserting_on" : False
}

folders = {
    "input":"/Users/vigneshsharma/Desktop/Financial_Chatbot/Financial_ChatBot/src/rag_agent/storage",
    "extracted":"intermediate/extracted",
    "processed":"intermediate/processed",
    "embedded":"prepared",
    "final":"prepared"
}

allowed_extentions = ['.pdf', '.txt', '.csv', '.docx']

processor_config = {
    "chunk_method":"page_number",
    "type_lowercase_match" : ['listitem','image','table','title','compositeelement'],
    "type_word_within":['text'],
    "type_table" : ['table'],
    "type_image":['image'],
    'clean_nltk':[],
    'clean_llm':['image','compositeelement'],
    'clean_llm_prompt':"Can you clean up the following text? Please only return the clean text with no headers or other informations.Some of the words may be overwritten vertically.If you can't find anything useful, please return an empty reponse. ***START TEXT***{content}***END TEXT***"
}