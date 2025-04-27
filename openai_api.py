import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# OpenAI API integration

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"

load_dotenv()

def get_openai_client():
    """Initialize and return OpenAI client with API key"""
    # Use the provided API key or get it from environment variables
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    return OpenAI(api_key=openai_api_key)

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

def upload_file_to_openai(file_path):
    """
    OpenAI API에 파일을 업로드합니다.
    
    Args:
        file_path: 업로드할 파일 경로
        
    Returns:
        file_id: 업로드된 파일의 ID
    """
    client = get_openai_client()
    
    try:
        with open(file_path, "rb") as file:
            response = client.files.create(
                file=file,
                purpose="user_data"
            )
            return response.id
    except Exception as e:
        raise Exception(f"파일 업로드 중 오류 발생: {str(e)}")

def delete_file_from_openai(file_id):
    """
    OpenAI API에서 파일을 삭제합니다.
    
    Args:
        file_id: 삭제할 파일의 ID
    """
    client = get_openai_client()
    
    try:
        client.files.delete(file_id=file_id)
        return True
    except Exception as e:
        print(f"파일 삭제 중 오류 발생: {str(e)}")
        return False
