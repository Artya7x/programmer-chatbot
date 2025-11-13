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
        
        **RULES**
        Please adhere to the schema you have been given. If you haven't reached a decision yet and the interview is still
        ongoing, put "N/A" in the decision attribute. Once you reach a decision put "1" or "0" in the decision attribute. 1 is for acceptance and 0 for denial.
        Your responses simply go to the response attribute as always.
        """
    return prompt