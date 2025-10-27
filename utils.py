"""
Utility functions for the AI Mock Interviewer Streamlit app.

This file contains all the backend logic, such as:
- Firebase initialization
- OpenRouter API client setup
- API calls for generating questions, feedback, and evaluations
- Database storage functions
"""

from datetime import datetime
from typing import List, Optional

import streamlit as st
import openai

try:
    import firebase_admin
    from firebase_admin import credentials, db
except ImportError:
    firebase_admin = None  # Firebase is optional


@st.cache_resource
def init_firebase() -> Optional[db.Reference]:
    """
    Initialises Firebase using credentials from Streamlit secrets.
    Safely handles cases where no secrets file is present.
    """
    if firebase_admin is None:
        st.sidebar.warning("Firebase library not installed. Database features disabled.")
        return None

    try:
        if "firebase_service_account" in st.secrets and "FIREBASE_DATABASE_URL" in st.secrets:
            creds_json = dict(st.secrets["firebase_service_account"])
            database_url = st.secrets["FIREBASE_DATABASE_URL"]

            if not firebase_admin._apps:
                cred = credentials.Certificate(creds_json)
                firebase_admin.initialize_app(cred, {"databaseURL": database_url})
            
            st.sidebar.success("Firebase connection established. 💾")
            return db.reference("/interviews")
        else:
            st.sidebar.info(
                "Firebase secrets not found. "
                "Interview sessions will not be saved."
            )
            return None
            
    except st.errors.StreamlitSecretNotFoundError:
        st.sidebar.info(
            "Running locally without secrets.toml. "
            "Firebase saving is disabled."
        )
        return None
    except Exception as e:
        st.sidebar.error(f"Firebase init failed: {e}")
        return None


@st.cache_resource
def get_openrouter_client(api_key: str) -> Optional[openai.Client]:
    """
    Creates and caches an OpenRouter client using the provided API key.
    Returns None if the API key is missing.
    """
    if not api_key:
        st.error("Please provide your OpenRouter API key in the sidebar.")
        return None
    
    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        return client
    except Exception as e:
        st.error(f"Failed to create API client: {e}")
        return None


def generate_question(
    client: openai.Client, 
    job_title: str, 
    model_name: str,
    max_questions: int,
    interview_type: str,
    previous_questions: List[str], 
    previous_answers: List[str]
) -> Optional[str]:
    """Generates the next interview question based on type and history."""
    
    system_prompt = (
        f"You are an expert interviewer for a {job_title} position. "
        f"You will conduct a mock interview with a total of {max_questions} questions. "
        "Ask one concise, relevant interview question at a time. "
        "Do not number your questions. "
        "Base your next question on the candidate's previous answers."
    )
    
    if interview_type == "Technical":
        system_prompt += (
            " This is a technical interview. "
            "Ask a technical question related to the job, testing their "
            "knowledge and problem-solving skills."
        )
    elif interview_type == "Behavioral (STAR format)":
        system_prompt += (
            " This is a behavioral interview. "
            "Ask a behavioral question that the user should answer using the STAR method. "
            "Start your question with 'Tell me about a time when...' or 'Describe a situation where...'"
        )
    else:
        system_prompt += " This is a general interview. Ask a common, non-technical question."

    messages = [{"role": "system", "content": system_prompt}]
    
    for q, a in zip(previous_questions, previous_answers):
        messages.append({"role": "assistant", "content": q})
        messages.append({"role": "user", "content": a})

    if not previous_questions:
        messages.append({"role": "user", "content": "Please ask me the first question."})
    else:
        messages.append({"role": "user", "content": "Please ask me the next question."})

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        question = response.choices[0].message.content.strip()
        return question
    
    except openai.AuthenticationError:
        st.error("Authentication Error: Please check your OpenRouter API key.")
        return None
    except openai.RateLimitError:
        st.error("Rate Limit Exceeded: Please wait and try again or check your plan.")
        return None
    except Exception as e:
        st.error(f"An API error occurred: {e}")
        return None


def get_feedback_for_answer(
    client: openai.Client, 
    model_name: str, 
    question: str, 
    answer: str
) -> Optional[str]:
    """Gets immediate, concise feedback for a single answer."""
    system_prompt = (
        "You are an expert interview coach. "
        "Provide 2-3 bullet points of constructive, concise feedback on the user's "
        "answer to the interview question. "
        "Focus on what they did well and how they could improve. "
        "Start with 'Here's some feedback on your answer:'"
    )
    user_prompt = f"Question: {question}\n\nAnswer: {answer}"

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error getting per-question feedback: {e}")
        return None


def evaluate_answers(
    client: openai.Client, 
    job_title: str,
    model_name: str, 
    questions: List[str], 
    answers: List[str]
) -> Optional[str]:
    """Evaluates the candidate’s overall performance."""
    
    system_prompt = (
        f"You are an expert hiring manager for a {job_title} position. "
        "Your task is to provide a final, overall evaluation of the candidate's "
        "performance based on the following interview transcript."
    )
    
    transcript = ""
    for i, (q, a) in enumerate(zip(questions, answers)):
        transcript += f"Question {i+1}: {q}\nAnswer {i+1}: {a}\n\n"
        
    user_prompt = (
        f"Here is the interview transcript:\n\n{transcript}"
        "Please provide a concise, overall evaluation of the candidate's performance. "
        "Focus on: \n1. Overall Strengths \n2. Key Areas for Improvement. \n\n"
        "Provide your final feedback in clear, constructive bullet points."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        result = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=500,
            temperature=0.5,
        )
        return result.choices[0].message.content.strip()
    
    except Exception as e:
        st.error(f"An API error occurred during evaluation: {e}")
        return None


def store_session(db_ref: Optional[db.Reference], session_data: dict) -> None:
    """Stores the interview session (including feedback) in Firebase."""
    if db_ref is None:
        print("Firebase not initialized. Skipping data storage.")
        return
    
    try:
        db_ref.push().set(session_data)
        st.success("Interview session saved to database.")
    except Exception as e:
        st.warning(f"Warning: Failed to store interview session: {e}")