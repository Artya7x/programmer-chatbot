from scripts.llm_inference import generate_response

MODEL_NAME = "gpt-4o"
def process_chat_query(query: str, conv_id: str, user_role: str):
    """Processes a user query by fetching sample data and querying the LLM."""

    prompt = build_prompt(query, user_role)
    response = generate_response(MODEL_NAME, prompt,conv_id)

    return response


def build_prompt(query, user_role):
    """Builds a structured prompt for the LLM with strict filtering instructions."""
    prompt = f"""
        **User Role:** "{user_role}"
        **User message:** "{query}"
        """
    return prompt