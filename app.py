import streamlit as st
from groq import Groq
import google.generativeai as genai
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ========================
# PAGE CONFIG
# ========================
st.set_page_config(page_title="ArsMindMate AI", layout="wide")

# ========================
# API KEYS (FROM SECRETS)
# ========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GROQ_API_KEY:
    st.error("Missing GROQ_API_KEY in secrets")
    st.stop()

# ========================
# API SETUP
# ========================
groq_client = Groq(api_key=GROQ_API_KEY)

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

# ========================
# SESSION STATE
# ========================
if "history" not in st.session_state:
    st.session_state.history = []

if "mode" not in st.session_state:
    st.session_state.mode = "friend"

if "moods" not in st.session_state:
    st.session_state.moods = []

# ========================
# AI RESPONSE
# ========================
def generate_ai_response(user_input):
    mode = st.session_state.mode

    if mode == "therapist":
        system = "You are a calm, empathetic therapist."
    elif mode == "coach":
        system = "You are a strict, direct coach."
    else:
        system = "You are a friendly emotional companion."

    try:
        chat = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_input}
            ],
            model="llama3-8b-8192"
        )
        response = chat.choices[0].message.content

    except:
        if GEMINI_API_KEY:
            try:
                prompt = f"{system}\nUser: {user_input}\nAI:"
                res = gemini_model.generate_content(prompt)
                response = res.text
            except Exception as e:
                return f"ERROR: {str(e)}"
        else:
            return "AI not available"

    # Mood tracking
    if any(w in user_input.lower() for w in ["sad", "lonely", "bad"]):
        st.session_state.moods.append(-1)
    elif any(w in user_input.lower() for w in ["happy", "good", "great"]):
        st.session_state.moods.append(1)
    else:
        st.session_state.moods.append(0)

    return response

# ========================
# UI STYLE
# ========================
st.markdown("""
<style>
.user {
    background:#2D8CFF;
    padding:10px;
    border-radius:10px;
    margin:5px;
    color:white;
}
.bot {
    background:#262730;
    padding:10px;
    border-radius:10px;
    margin:5px;
    color:white;
}
</style>
""", unsafe_allow_html=True)

# ========================
# HEADER
# ========================
st.title("🧠 ArsMindMate AI")
st.caption("Smart Emotional Chatbot")

# ========================
# SIDEBAR
# ========================
with st.sidebar:
    st.header("⚙️ Settings")

    st.session_state.mode = st.selectbox(
        "Personality",
        ["friend", "therapist", "coach"]
    )

    if st.session_state.moods:
        fig, ax = plt.subplots()
        ax.plot(st.session_state.moods, marker='o')
        ax.set_title("Mood Trend")
        st.pyplot(fig)

# ========================
# CHAT DISPLAY
# ========================
for chat in st.session_state.history:
    st.markdown(f"<div class='user'>👤 {chat['user']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='bot'>🧠 {chat['bot']}</div>", unsafe_allow_html=True)

# ========================
# INPUT
# ========================
user_input = st.chat_input("Talk to ArsMindMate...")

if user_input:
    response = generate_ai_response(user_input)

    st.session_state.history.append({
        "user": user_input,
        "bot": response,
        "time": datetime.now().strftime("%H:%M")
    })

    st.rerun()