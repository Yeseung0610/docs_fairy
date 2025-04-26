import os
from openai import OpenAI

# OpenAI API integration

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

def get_openai_client():
    """Initialize and return OpenAI client with API key"""
    # Use the provided API key or get it from environment variables
    api_key = os.getenv("OPENAI_API_KEY", os.environ.get('OPENAI_API_KEY'))
    return OpenAI(api_key=api_key)

def get_ai_response(messages):
    """Get a response from the OpenAI API"""
    client = get_openai_client()
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting AI response: {str(e)}"
