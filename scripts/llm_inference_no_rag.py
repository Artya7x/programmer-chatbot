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


class OptimizationResponse(BaseModel):
    python_code: str
    reasoning: str

def generate_optimization(model, prompt, conversation_id):
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
            instructions="""
            You are a Python optimization assistant trained through natural language instructions provided by the instructor.

            Your role is to **analyze and optimize Python code** that may contain poor naming conventions and deeply nested conditional logic.

            ### Objective
            Receive a piece of Python code (via text or uploaded file) and produce:
            1. An optimized version of the same code.
            2. A clear explanation of what changes you applied and why.

            ### Optimization Rules
            1. **Variable Naming**
               - Rename variables automatically according to this convention:
                 - Integers → `intVar_#`
                 - Floats → `floatVar_#`
                 - Strings → `strVar_#`
                 - Lists → `listVar_#`
                 - Dictionaries → `dictVar_#`
                 - Booleans → `boolVar_#`
                 - Other types → `var_#`
               - Preserve logic and data types exactly as in the original code.
               - Ensure the new names follow the convention consistently across all scopes.

            2. **Nested IF Detection**
               - Detect any nested `if` statements deeper than three levels.
               - Add a comment above each such block:
                 `# Deeply nested conditional (>3 levels)`
               - Do not change their logic, only mark them.

            ### Output Format
            Return your output in the following JSON structure:
            {
              "python_code": "<optimized Python code>",
              "reasoning": "<short explanation of the improvements>"
            }

            ### Behavior
            - Do NOT invent additional functionality.
            - Keep all code logically equivalent to the original.
            - Maintain consistent indentation and valid Python syntax.
            """,

            input=prompt,
            conversation=conversation_id,
            text_format=OptimizationResponse
        )
        print(response.output_parsed)
        return response.output_parsed

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"