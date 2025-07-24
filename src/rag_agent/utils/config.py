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