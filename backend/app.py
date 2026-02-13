import streamlit as st
import os
import sqlite3
import hashlib
from google import genai
from dotenv import load_dotenv

load_dotenv()

# --- DATABASE LOGIC ---
def init_db():
    conn = sqlite3.connect('assistant.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, level TEXT)')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def create_user(username, password):
    conn = sqlite3.connect('assistant.db')
    c = conn.cursor()
    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (username, make_hashes(password)))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('assistant.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE username =?', (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

init_db()

# --- UI STYLING ---
st.set_page_config(page_title="AI Teaching Assistant", layout="centered")

# FIXED: Removed the incorrect keyword argument
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 80px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- APP FLOW ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_level' not in st.session_state:
    st.session_state.user_level = None

if not st.session_state.logged_in:
    st.title("🎓 AI Teaching Assistant")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid Username/Password")

    with tab2:
        new_user = st.text_input("New Username")
        new_password = st.text_input("New Password", type='password')
        if st.button("Register"):
            try:
                create_user(new_user, new_password)
                st.success("Account created! Please Login.")
            except:
                st.error("Username already exists.")

else:
    # MAIN APP UI
    st.title(f"Welcome, {st.session_state.username}!")
    st.subheader("Select your learning level:")

    # FOUR BOX SELECTION
    col1, col2, col3, col4 = st.columns(4)
    if col1.button("🏫\nPrimary"): st.session_state.user_level = "Primary School"
    if col2.button("🎓\nSecondary"): st.session_state.user_level = "Higher Secondary"
    if col3.button("🏛️\nCollege"): st.session_state.user_level = "College"
    if col4.button("🔬\nPhD"): st.session_state.user_level = "PhD"

    if st.session_state.user_level:
        st.info(f"Current Mode: {st.session_state.user_level} Tutor")
        
        # Simple Chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Ask a question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Use Gemini API
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            with st.spinner("Tutor is thinking..."):
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=f"You are a {st.session_state.user_level} teaching assistant. {prompt}"
                )
                st.chat_message("assistant").write(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})