import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from groq import Groq  # Nayi library

# --- AI SETUP ---
# Pehle Secrets se key dhoondo, nahi toh sidebar se lo
api_key_to_use = ""

if "GROQ_API_KEY" in st.secrets:
    api_key_to_use = st.secrets["GROQ_API_KEY"]
elif user_api_key:
    api_key_to_use = user_api_key

if api_key_to_use:
    client = Groq(api_key=api_key_to_use)
else:
    client = None

def get_ai_advice(task_name, category):
    if not client:
        return "Pehle Sidebar mein API Key daalein!"
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a Gen-AI Mentor. Give a 2-line practical study tip in Hinglish."},
                {"role": "user", "content": f"Topic: {task_name}"}
            ],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}" # Ye line asli error batayegi

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, task TEXT, category TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- APP UI ---
st.set_page_config(page_title="Gen-AI Tracker + AI Coach", page_icon="🤖")
st.title("🤖 Gen-AI Smart Tracker")

# Sidebar
st.sidebar.title("Settings")
user_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
if user_api_key:
    client = Groq(api_key=user_api_key)

# Input Form
with st.expander("➕ Naya Task Add Karein"):
    t_name = st.text_input("Topic Name")
    t_cat = st.selectbox("Stage:", ["Step 0: Python", "Step 1: Basics", "Step 2: RAG/Agents", "Step 3: Deploy"])
    if st.button("Save"):
        conn = sqlite3.connect('routine_tracker.db')
        c = conn.cursor()
        c.execute("INSERT INTO tasks (date, task, category, status) VALUES (?, ?, ?, ?)",
                  (datetime.now().strftime("%Y-%m-%d"), t_name, t_cat, "Pending"))
        conn.commit()
        st.rerun()

# Display Tasks
st.subheader("📑 Aapka Learning Log")
conn = sqlite3.connect('routine_tracker.db')
df = pd.read_sql_query("SELECT * FROM tasks WHERE status = 'Pending'", conn)
conn.close()

for index, row in df.iterrows():
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{row['task']}**")
        with col2:
            if st.button("Get AI Tip 💡", key=f"ai_{row['id']}"):
                advice = get_ai_advice(row['task'], row['category'])
                st.info(advice)
        
        if st.button("Done ✅", key=f"done_{row['id']}"):
            conn = sqlite3.connect('routine_tracker.db')
            c = conn.cursor()
            c.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (row['id'],))
            conn.commit()
            st.rerun()
