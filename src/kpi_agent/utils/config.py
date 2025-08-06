AGENT_NAME = "SQL-Agent"
insert_chat_query = """ 
INSERT INTO chat_sessions (session_id, chat_id, source_agent, prompt_text, created_at) 
VALUES (%s, %s, %s, %s, UTC_TIMESTAMP()) 
""" 

chat_session = """
CREATE TABLE chat_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    chat_id VARCHAR(100),
    source_agent VARCHAR(100),
    prompt_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

tableschema = """
CREATE TABLE ffoh (
    US_Plant VARCHAR(100),
    Plant_No VARCHAR(20),
    Actual_Costs DECIMAL(18,2),
    Plan_Costs DECIMAL(18,2),
    Cost_Center_Description VARCHAR(255),
    Cost_Center VARCHAR(50),
    Cost_Element_Description VARCHAR(255),
    Sender_Receiver_Level_01 VARCHAR(100),
    Month VARCHAR(20),
    Year INT,
    GL_Account VARCHAR(50),
    ID VARCHAR(100),
    Category VARCHAR(100)
);
"""

cte = """
WITH FFOH_Component_Detail_Summary AS (
    SELECT
        Division,
        Factory,
        Cost_Center,
        Cost_Center_Description,
        GL_Account,
        Cost_Element_Description,
        Month,
        Year,
        Category,
        SUM([Actual Costs]) AS Total_Actual_Costs
    FROM FFOH_Data
    GROUP BY 
        Division, Factory, Cost_Center, Cost_Center_Description,
        GL_Account, Cost_Element_Description, Month, Year, Category
)
"""