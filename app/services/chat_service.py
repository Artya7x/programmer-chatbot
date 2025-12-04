from scripts.llm_inference import generate_response
from scripts.llm_inference_no_rag import generate_optimization
MODEL_NAME = "gpt-4o"


def process_chat_query(query: str, conv_id: str, user_role:str):
    """Processes a user query by fetching sample data and querying the LLM."""

    prompt = build_prompt(query)
    if user_role == "generate code":
        response = generate_response(MODEL_NAME, prompt, conv_id)
    elif user_role == "optimize code":
        response = generate_optimization(MODEL_NAME,prompt,conv_id)
    return response


def build_prompt(query ):
    """Builds a structured prompt for the LLM with strict filtering instructions."""
    prompt = f"""
        
        **User message:** "{query}"

        
        """
    return prompt