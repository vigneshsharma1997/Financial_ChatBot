import os 
import sys 
import time 
from typing import List 
from common.LLM_Client import llm_model 
from dotenv import load_dotenv 
from agent.service_discovery import get_business_solutions 
 
load_dotenv() 
 
from pathlib import Path 
 
systemp_prompt_path = Path("D:/code/propelops/my_project_template/ORCHESTRATOR_ROUTER/storage/LLM_Routing_Prompt.txt") 
 
class AgentRouting(object): 
    """ 
    A class to determine which services to invoke using a language model prompt. 
    """ 
    VALID_SERVICES = ["KPI_RCA","KPI_INSIGHT"] 
 
    def __init__(self): 
        self.llm_client = llm_model() 
        self.system_prompt = systemp_prompt_path 
 
    def generate_prompt(self,user_query)->str: 
        agent_information = "" 
        business_solution = get_business_solutions()  #Load service configurations from JSON file 
        print("Business Solution: ",business_solution) 
        with open(self.system_prompt,'r',encoding='utf-8') as file: 
            template = file.read() 
        for service_name,metadata in business_solution.items(): 
            if not (metadata['description'] is None or metadata['description']==""): 
                agent_information += "\nAgent Name:" + service_name +"\n" 
                agent_information += metadata["description"] + "\n" 
        completed_prompt = template.format(user_query=user_query,agent_information=agent_information) 
        print("Completed_Prompt : ",completed_prompt) 
        return completed_prompt 
 
    def get_service_to_invoke(self,user_query,retries=3) -> List[str]: 
        for attempt in range(retries): 
            try : 
                print("Inside get service to invoke.") 
                prompt = self.generate_prompt(user_query) 
                response = self.llm_client.invoke(prompt) 
                services_string = response.content.strip() 
                services = [services_string] if isinstance(services_string, str) else services_string        
                print("Service ",services) 
                # invalid_service = [service for service in services if service not in self.VALID_SERVICES] 
                # if invalid_service: 
                #     raise ValueError(f"Invalid service : {', '.join(invalid_service)}") 
                 
                return services 
             
            except(KeyError,ValueError) as e: 
                if attempt<retries -1 : 
                    time.sleep(1) 
                else: 
                    return [] 
 
 
    def select_service(self, user_query,method) -> List[str]: 
        if method == 'llm': 
            print(f"User Query : {user_query} , Method : {method}") 
            services_to_call = self.get_service_to_invoke(user_query) 
     
            return services_to_call 