from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel


# Load environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Error: Missing OpenAI API Key. Set it in .env or as an environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)

class ModelResponse(BaseModel):
    python_code : str
    cfg_graph : str
    dfg_graph : str
    reasoning: str


def generate_response(model, prompt, conversation_id):
    """
    Generate a response using OpenAI API with Structured Outputs.

    Args:
        model (str): The model name.
        prompt (str): The user's query.
        conversation_id (str): The id of the current conversation. This is how the LLM knows context.
    """

    try:
        response = client.responses.parse(
            model=model,
            instructions ="""
            
            Role:
                You are an intelligent programming assistant. Your purpose is to generate Python code, a Control Flow Graph (CFG), and a Data Flow Graph (DFG) based on natural language descriptions provided by the user.
            
            Task:
                When a user provides a functional description in natural language:

                    1) Search the knowledge base for relevant information or examples related to the requested functionality.

                    2) Use the retrieved knowledge to guide your reasoning and code generation.

                    3) Produce the following outputs:

                       3.1) Valid and complete Python function code.

                       3.2) A Control Flow Graph (CFG) written in Graphviz DOT format that represents the execution order of the function’s statements.

                       3.3) A Data Flow Graph (DFG) written in Graphviz DOT format that represents how data and variables are defined and used within the function.
                    
            Response Format : 
            
                {
                    "python_code": "<Python function code>",
                    "cfg_graph": "<Control Flow Graph in Graphviz DOT format>",
                    "dfg_graph": "<Data Flow Graph in Graphviz DOT format>"
                }
                
            Behavior Rules:
                1) Always search and use the knowledge base before generating an answer.
                2) Both graphs must follow the Graphviz DOT syntax (e.g., start with digraph CFG { ... } and digraph DFG { ... }).
                3) Ensure the JSON is syntactically valid and contains only the three required keys
                4) When you provide the code and the graphs, please write a small description of what you give to the user
            """,

            input=prompt,
            conversation = conversation_id,
            tools=[{
                "type": "file_search",
                "vector_store_ids": ["vs_6910d22afa4081918b2009351a3af3da"]
            }],
            text_format=ModelResponse
        )
        print(response.output_parsed)
        return response.output_parsed

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"