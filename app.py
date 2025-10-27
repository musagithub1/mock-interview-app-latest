"""
Streamlit application for an AI-powered mock interview.

This improved script (v5) integrates several new features:
- **App Navigation:** A sidebar radio button to switch between the
  "Start Interview" app and a new "My Interview History" page.
- **Interview Types:** Users can select "General", "Technical", or
  "Behavioral" to change the style of the interview.
- **Chat History:** The UI now uses `st.chat_message` to display the
  full conversation history.
- **Per-Question Feedback:** After each answer, the AI provides
  immediate, concise feedback, which is displayed in the chat.
"""

import os
from datetime import datetime
from typing import List, Optional

import streamlit as st
import openai  # Keep using the openai library, it's compatible

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
    
    # --- UPDATED PROMPT with Interview Type ---
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


# --- NEW FUNCTION (Feature 2) ---
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


# --- NEW FUNCTION (Feature 4) ---
def show_interview_history(db_ref: Optional[db.Reference]):
    """Displays a list of past interviews from Firebase."""
    st.title("My Interview History 📜")

    if db_ref is None:
        st.error("Firebase is not connected. Cannot show history.")
        st.info("Please set up your `secrets.toml` with Firebase credentials to use this feature.")
        return

    try:
        interviews = db_ref.get()
        if not interviews:
            st.info("No past interviews found in the database.")
            return
        
        # Sort interviews by timestamp, newest first
        sorted_interviews = sorted(
            interviews.items(), 
            key=lambda item: item[1].get("timestamp", ""), 
            reverse=True
        )

        for session_id, session_data in sorted_interviews:
            # Handle potential missing data gracefully
            job_title = session_data.get('job_title', 'Unknown Job')
            timestamp = session_data.get('timestamp', 'Unknown Time')
            model = session_data.get('model', 'N/A')
            
            try:
                # Format timestamp for display
                date_obj = datetime.fromisoformat(timestamp)
                display_time = date_obj.strftime('%B %d, %Y at %I:%M %p')
            except ValueError:
                display_time = timestamp

            with st.expander(f"**{job_title}** - {display_time}"):
                st.write(f"**Model Used:** {model}")
                
                st.subheader("Final Evaluation")
                st.markdown(session_data.get('evaluation', 'No evaluation found.'))
                
                st.subheader("Full Transcript & Feedback")
                questions = session_data.get('questions', [])
                answers = session_data.get('answers', [])
                feedback_list = session_data.get('feedback', [])

                for i in range(len(questions)):
                    with st.chat_message("assistant"):
                        st.markdown(f"**Q:** {questions[i]}")
                    
                    if i < len(answers):
                        with st.chat_message("user"):
                            st.markdown(f"**A:** {answers[i]}")
                    
                    if i < len(feedback_list) and feedback_list[i]:
                        with st.chat_message("assistant", avatar="🧑‍🏫"):
                            st.markdown(f"**Feedback:** {feedback_list[i]}")
                    st.divider()

    except Exception as e:
        st.error(f"An error occurred while fetching interview history: {e}")


# --- UPDATED FUNCTION ---
def run_interview_app(
    db_ref: Optional[db.Reference],
    api_key: str,
    model_name: str,
    max_questions: int,
    user_name: str,
    job_title: str,
    interview_type: str
):
    """Main logic for running the interview session."""
    st.title(f"🧠 {job_title} Mock Interview")
    st.write(f"**Type:** {interview_type} | **Length:** {max_questions} Questions")
    st.divider()

    # Initialize session state variables
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.evaluation = ""
        st.session_state.client = None
        st.session_state.max_questions = 3
        st.session_state.feedback = [] # New state for per-question feedback

    # "Start Interview" button
    if st.button("Start Interview", disabled=st.session_state.interview_started):
        if api_key and job_title:
            client = get_openrouter_client(api_key)
            if client:
                # Reset session state for a new interview
                st.session_state.questions = []
                st.session_state.answers = []
                st.session_state.feedback = [] # Clear feedback
                st.session_state.evaluation = ""
                st.session_state.client = client
                st.session_state.job_title = job_title
                st.session_state.max_questions = max_questions
                
                with st.spinner("Generating first question..."):
                    question = generate_question(
                        client=client,
                        job_title=job_title,
                        model_name=model_name,
                        max_questions=max_questions,
                        interview_type=interview_type, # Pass new param
                        previous_questions=[],
                        previous_answers=[]
                    )
                
                if question:
                    st.session_state.questions.append(question)
                    st.session_state.interview_started = True
                    st.rerun() # Rerun to display the chat UI
                else:
                    st.error("Failed to start interview. Check API key or model choice.")
        else:
            st.warning("Please enter your API Key and a Job Title in the sidebar.")

    # --- NEW (Feature 1): Display Chat History ---
    if st.session_state.interview_started:
        for i in range(len(st.session_state.answers)):
            # Question
            with st.chat_message("assistant"):
                st.markdown(st.session_state.questions[i])
            # Answer
            with st.chat_message("user"):
                st.markdown(st.session_state.answers[i])
            # Feedback
            if i < len(st.session_state.feedback) and st.session_state.feedback[i]:
                with st.chat_message("assistant", avatar="🧑‍🏫"):
                    st.markdown(st.session_state.feedback[i])
        
        # Display the last question (the one to be answered)
        if len(st.session_state.questions) > len(st.session_state.answers):
             with st.chat_message("assistant"):
                st.markdown(st.session_state.questions[-1])


    # Interview in progress
    if st.session_state.interview_started and not st.session_state.evaluation:
        current_q_index = len(st.session_state.answers)
        
        # Check if there is a new question to be answered
        if current_q_index < len(st.session_state.questions):
            with st.form(key=f"answer_form_{current_q_index}"):
                answer = st.text_area("Your answer:", key=f"answer_{current_q_index}")
                submit_button = st.form_submit_button("Submit Answer")

                if submit_button:
                    if answer.strip():
                        st.session_state.answers.append(answer)
                        
                        # --- NEW (Feature 2): Get per-question feedback ---
                        with st.spinner("Analyzing your answer..."):
                            feedback = get_feedback_for_answer(
                                client=st.session_state.client,
                                model_name=model_name,
                                question=st.session_state.questions[current_q_index],
                                answer=answer
                            )
                        st.session_state.feedback.append(feedback) # Store feedback

                        # --- End of Feedback logic ---

                        next_q = None
                        if len(st.session_state.answers) < st.session_state.max_questions:
                            with st.spinner("Generating next question..."):
                                next_q = generate_question(
                                    client=st.session_state.client,
                                    job_title=st.session_state.job_title,
                                    model_name=model_name,
                                    max_questions=st.session_state.max_questions,
                                    interview_type=interview_type, # Pass new param
                                    previous_questions=st.session_state.questions,
                                    previous_answers=st.session_state.answers,
                                )
                            
                            if next_q:
                                st.session_state.questions.append(next_q)
                            else:
                                st.session_state.answers.pop()
                                st.session_state.feedback.pop() # Remove feedback if Q fails
                                st.error(
                                    "Error generating the next question (API call failed). "
                                    "Please try submitting your answer again."
                                )
                            
                        else: # This is the last question
                            with st.spinner("Evaluating your performance..."):
                                evaluation = evaluate_answers(
                                    client=st.session_state.client,
                                    job_title=st.session_state.job_title,
                                    model_name=model_name,
                                    questions=st.session_state.questions,
                                    answers=st.session_state.answers,
                                )
                            if evaluation:
                                st.session_state.evaluation = evaluation
                                session_data = {
                                    "user": user_name or "Anonymous",
                                    "job_title": st.session_state.job_title,
                                    "questions": st.session_state.questions,
                                    "answers": st.session_state.answers,
                                    "feedback": st.session_state.feedback, # Save feedback
                                    "evaluation": evaluation,
                                    "model": model_name,
                                    "timestamp": datetime.utcnow().isoformat(),
                                }
                                store_session(db_ref, session_data)
                            else:
                                st.error("Failed to get final evaluation.")
                        
                        if next_q or len(st.session_state.answers) == st.session_state.max_questions:
                            st.rerun()
                    else:
                        st.warning("Please provide an answer.")

    # Show final evaluation after interview is complete
    if st.session_state.evaluation:
        st.success("Interview completed!")
        st.subheader("Your Final Feedback")
        st.markdown(st.session_state.evaluation)

        # The transcript is already visible in the chat history,
        # but an expander is still good for a clean final summary.
        with st.expander("View Full Interview Summary (incl. Final Evaluation)"):
            st.markdown(st.session_state.evaluation)
            st.divider()
            st.markdown("For the full transcript with per-question feedback, see the chat history above.")

        if st.button("Start a New Interview"):
            st.session_state.clear()
            st.rerun()


# --- NEW Main function to handle navigation ---
def main():
    """Main entry point for the app, handles navigation."""
    st.set_page_config(page_title="AI Mock Interviewer", layout="wide")

    # --- Sidebar Configuration (now in main) ---
    st.sidebar.header("Configuration")
    
    try:
        default_api_key = st.secrets.get("OPENROUTER_API_KEY")
    except st.errors.StreamlitSecretNotFoundError:
        default_api_key = "" 

    api_key = st.sidebar.text_input(
        "Enter your OpenRouter API Key", 
        type="password",
        value=default_api_key, 
        help="You can also set this as `OPENROUTER_API_KEY` in your Streamlit secrets."
    )
    
    model_name = st.sidebar.selectbox(
        "Select AI Model",
        (
            "z-ai/glm-4.5-air",
            "openai/gpt-3.5-turbo",
            "google/gemini-pro",
            "mistralai/mistral-7b-instruct-v0.3",
            "anthropic/claude-3-haiku-20240307"
        ),
        index=0,
        help="Some models may be free, others require OpenRouter credits."
    )
    
    max_questions = st.sidebar.number_input(
        "Number of Questions", 
        min_value=1, 
        max_value=10, 
        value=3
    )
    
    user_name = st.sidebar.text_input("Your Name (Optional, for saving)")
    job_title = st.sidebar.text_input("Interview Job Title (e.g., Software Engineer)")
    
    # --- NEW (Feature 3) ---
    interview_type = st.sidebar.selectbox(
        "Select Interview Type",
        ("General", "Technical", "Behavioral (STAR format)")
    )
    
    st.sidebar.divider()
    
    # Initialise Firebase (once for the whole app)
    db_ref = init_firebase()

    # --- NEW (Feature 4) ---
    app_mode = st.sidebar.radio(
        "Navigation", 
        ["Start Interview", "My Interview History"]
    )

    if app_mode == "Start Interview":
        run_interview_app(
            db_ref=db_ref,
            api_key=api_key,
            model_name=model_name,
            max_questions=max_questions,
            user_name=user_name,
            job_title=job_title,
            interview_type=interview_type
        )
    elif app_mode == "My Interview History":
        show_interview_history(db_ref)


if __name__ == "__main__":
    main()