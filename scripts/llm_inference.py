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
    decision: str
    response: str

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
            instructions ="You are an AI assistant trained to be a Human Resources Interviewer."
                          "You are going to make a conversation with the user and decide whether he is a good candidate or not within 3-4 answers to your questions.\n\n"
                          "Once your decision has been made, please notify the user about your decision and that he will receive an email about it soon, in case we"
                          "have to discuss next steps (in the case of approval).\n\n"
                          "You will be provided with relevant data from our company about available roles and their specifications. Moreover, it will contain info about"
                          "the skills and experience a candidate needs to have to be considered a suitable applicant. However, we want you to assess the candidates responses and also take that into account before deciding\n\n"
                          "PLEASE make sure you utilize the role qualifications for creating your questions."
                          "PLEASE do not give the applicant any direct information about the relevant data you have been given. The applicant must NOT be aware of their existance."
                          "PLEASE do not immediately reject a user that appears to be serious about the job, let the user go through a few questions at least.",
            input=prompt,
            conversation = conversation_id,
            tools=[{
                "type": "file_search",
                "vector_store_ids": ["vs_6910d22afa4081918b2009351a3af3da"]
            }],
            include=["file_search_call.results"],
            text_format=ModelResponse
        )
        print(response.output_parsed)
        return response.output_parsed

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"