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
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": " You are an AI assistant trained on HDFS data. Identify the most relevant data sources."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"
