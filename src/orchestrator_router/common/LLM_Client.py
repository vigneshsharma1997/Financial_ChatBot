from langchain_core.prompts import PromptTemplate 
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser 
from langchain_groq import ChatGroq 
import os 
from dotenv import load_dotenv 
load_dotenv() 
groq_api_key = os.getenv("GROQ_API_KEY") 
os.environ["LANGCHAIN_TRACING_V2"] = "false" 
 
def llm_model():   
    # LangGroq model (via LangChain interface) 
    llm = ChatGroq(model="Gemma2-9b-It",groq_api_key=groq_api_key) 
    return llm 
 
 
