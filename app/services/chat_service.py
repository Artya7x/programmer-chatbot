from scripts.llm_inference import generate_response

MODEL_NAME = "gpt-4o"
def process_chat_query(query: str):
    """Processes a user query by fetching sample data and querying the LLM."""

    prompt = build_prompt(query)
    response = generate_response(MODEL_NAME, prompt)

    return response


def build_prompt(query):
    """Builds a structured prompt for the LLM with strict filtering instructions."""
    prompt = f"""
        **User message:** "{query}"
        
        **RULES**
        
        """

    prompt += "\n****."
    return prompt