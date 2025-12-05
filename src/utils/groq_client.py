import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set in environment")

client = Groq(api_key=GROQ_API_KEY)

def chat(messages):
    """
    messages: list of dicts {"role":..., "content":...}
    returns string content from assistant
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )
    return response.choices[0].message.content
