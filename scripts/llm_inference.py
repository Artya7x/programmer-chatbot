from openai import OpenAI
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Error: Missing OpenAI API Key. Set it in .env or as an environment variable.")

client = OpenAI(api_key=OPENAI_API_KEY)



def generate_response(model, prompt):
    """
    Generate a response using OpenAI API with Structured Outputs.

    Args:
        model (str): The model name.
        prompt (str): The user's query.

    """
    try:
        response = client.responses.create(
            model=model,
            instructions ="You are an AI assistant trained to be a Human Resources Interviewer."
                          "You are going to make a conversation with the user and decide whether he is a good candidate or not within 3-4 answers to your questions."
                          "Once the use",
            input=prompt
        )

        return response.output_text

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"
