from common.database_connection import read_from_session_chat
import pandas as pd

def answer_to_llm(payload:dict,session_chat_data:pd.DataFrame,n:int=5)->dict:
    """
        Answer if the users' input requires a visual representation by interacting with an LLM.
        Args : 
            payload (dict) : The input data containing the 'output_prompt' for the LLM call.
            session_chat_data (pd.Dataframe) : DataFrame containing historical session data.
            n(int): Number of historical records to consider (default is 5). 
        Returns: 
            dict: A dictionary indicating whether the user's input requires a visual representation. 
    """
    llm = LLMCallModule()
    if 'user_query' not in payload:
        print("User Query key is missing from the payload.")
        raise KeyError("User query is missing in payload.")
    instruction_prompt = create_instruction_prompt(payload['user_query'],session_chat_data[:n])
    


def process_session_chat_data(payload:dict):
    """
        Reads and processes session data.
        Args : 
            payload(dict): The input data containing session and source agent information.

        Return : 
            pd.DataFrame : Processed session chat data or an empty DataFrame.
    """
    session_chat_data = read_from_session_chat(payload)
    if session_chat_data.empty:
        print("Sesion has no data.")
        return pd.DataFrame()

    session_chat_data = session_chat_data[session_chat_data['source_agent']] == payload['source_agent']
    if session_chat_data.empty:
        print("No relevant session data for this source.")
        return pd.DataFrame()
    session_chat_data.dropna(subset=['response_text'],inplace=True)
    session_chat_data['created_at'] = pd.to_datetime(session_chat_data['created_at'])
    session_chat_data.sort_values(by="created_at",inplace=True,ascending=True)
    session_chat_data.reset_index(inplace=True,drop=True)
    print("Session history is ready...")
    return session_chat_data

def answer_from_existing_data(payload:dict)->dict:
    """
        Retrieves data from an existing session_chat,process it and return the most relevant historical data.
        Args: 
            payload(dict) : The input data containing session and source agent information.
        Returns:
            dict: Dictionary containing the historical data or a flag indicating no relevant data.
    """
    response = {"can_answer":False}
    try : 
        session_chat_data = process_session_chat_data(payload)
        if session_chat_data.empty:
            return response
        llm_response = answer_to_llm(payload,session_chat_data)
        if isinstance(llm_response,dict):
            formatted_data = extract_from_llm_response(llm_response.get('answer',''))
            response['can_answer'] = formatted_data.get('can_answer',False)
            response['output'] = formatted_data.get('output',"")
    except Exception as e:
        print(f"Error in answer from existing data : {e}")
    print(f"Returning response from session data: {response}")
    return response