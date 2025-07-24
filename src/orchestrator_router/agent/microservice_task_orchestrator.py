from agent.service_discovery import get_business_solutions 
import httpx 
 
async def trigger_microservice_task(url,params)->str: 
    try: 
        print("Inside Trigger Microservice url : ",url) 
        print("Params ",params) 
        async with httpx.AsyncClient() as client: 
            response = await client.post(url, json=params) 
        # return response.raise_for_status() 
        return response.content 
    except httpx.HTTPStatusError as e: 
        print(f"HTTP error occured : {e}") 
        raise 
    except Exception as e: 
        print(f"An error occured while triggering microservice task: {e}") 
        raise 
 
async def trigger_selected_microservices(services,service_params) -> dict: 
    task_ids = {} 
    try: 
        services_urls = get_business_solutions() 
        for service in services: 
            if service in services_urls: 
                url = services_urls[service]["url"] 
                task_id = await trigger_microservice_task(url,service_params) 
                task_ids[service] = task_id 
            elif service in services_urls: 
                task_ids[service] = "Non_celery_Task" 
    except Exception as e: 
        print(f"An error occurred while triggering selected microservices: {e}") 
        raise 
    return task_ids 