AGENT_NAME="rag-agent"
document_pipeline_config = {
    "extracting_on" : False,
    "processing_on" : False,
    "embedding_on" : False,
    "upserting_on" : False
}
folders = {
    "input":"raw",
    "extracted":"intermediate/extracted",
    "processed":"intermediate/processed",
    "embedded":"prepared",
    "final":"prepared"
}

allowed_extentions = ['.docx, .pptx, .pdf']