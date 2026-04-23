import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from groq import Groq
import PyPDF2  # PDF padhne ke liye
import sys
from io import StringIO

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

# --- PDF RAG LOGIC ---
# Ye function PDF se roadmap padhega
def get_roadmap_context():
    try:
        with open("roadmap.pdf", "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except:
        return "Roadmap PDF nahi mili. Step 0-3 follow karein."

# --- APP CONFIG ---
st.set_page_config(page_title="Gen-AI Ultimate Tracker", layout="wide", page_icon="🚀")

# --- SIDEBAR: SETTINGS & MOTIVATION ---
st.sidebar.title("⚙️ AI Control Room")
user_api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if user_api_key:
    client = Groq(api_key=user_api_key)
    if st.sidebar.button("Aaj ki Motivation ✨"):
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Give a 1-line motivational kick in Hinglish for a Gen-AI student."}]
        )
        st.sidebar.info(resp.choices[0].message.content)
else:
    client = None
    st.sidebar.warning("Pehle API Key daalein!")

# --- MAIN INTERFACE ---
st.title("🤖 Gen-AI Pro Learning Workspace")

tab1, tab2, tab3 = st.tabs(["📊 Daily Tracker", "💻 Code Playground", "📖 Roadmap AI Chat"])

# --- TAB 1: TRACKER ---
with tab1:
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.subheader("Add New Task")
        t_name = st.text_input("Topic Name", placeholder="e.g. RAG Basics")
        t_cat = st.selectbox("Stage", ["Step 0: Python", "Step 1: Basics", "Step 2: Advanced", "Step 3: Deploy"])
        if st.button("Save Task"):
            if t_name:
                conn = sqlite3.connect('routine_tracker.db')
                c = conn.cursor()
                c.execute("INSERT INTO tasks (date, task, category, status) VALUES (?, ?, ?, ?)",
                          (datetime.now().strftime("%Y-%m-%d"), t_name, t_cat, "Pending"))
                conn.commit()
                st.rerun()

    with col_b:
        st.subheader("Pending Tasks")
        conn = sqlite3.connect('routine_tracker.db')
        df = pd.read_sql_query("SELECT * FROM tasks WHERE status = 'Pending'", conn)
        for idx, row in df.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['task']}**")
            if c2.button("AI Tip 💡", key=f"tip_{row['id']}"):
                if client:
                    tip_resp = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": f"Give a 2-line Hinglish tip for: {row['task']}"}]
                    )
                    st.info(tip_resp.choices[0].message.content)
            if c3.button("Done ✅", key=f"done_{row['id']}"):
                c.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (row['id'],))
                conn.commit()
                st.rerun()
        conn.close()

# --- TAB 2: CODE PLAYGROUND ---
with tab2:
    st.subheader("🐍 Python Live Editor")
    st.write("Apna code yahan likhein aur output dekhein:")
    code = st.text_area("Code Editor:", value="print('Hello World')\na = 10\nb = 20\nprint(f'Sum is: {a+b}')", height=200)
    if st.button("Run Code ▶️"):
        try:
            old_stdout = sys.stdout
            redirected_output = sys.stdout = StringIO()
            exec(code)
            sys.stdout = old_stdout
            st.success("Output:")
            st.code(redirected_output.getvalue())
        except Exception as e:
            st.error(f"Error: {e}")

# --- TAB 3: ROADMAP ASSISTANT (RAG) ---
with tab3:
    st.subheader("🧠 Roadmap Assistant")
    st.write("AI aapke `roadmap.pdf` ke hisaab se jawab dega.")
    user_ques = st.text_input("Apne roadmap ke baare mein puchiye (e.g. Agle mahine kya seekhna hai?)")
    
    if user_ques:
        if client:
            roadmap_text = get_roadmap_context()
            rag_prompt = f"Using this Roadmap Content: {roadmap_text}\nAnswer the user: {user_ques}"
            
            with st.spinner("AI thinking..."):
                resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "You are a Roadmap Expert. Answer in Hinglish based ONLY on the provided roadmap context."},
                              {"role": "user", "content": rag_prompt}]
                )
                st.write("🤖 AI Mentor:", resp.choices[0].message.content)
        else:
            st.error("Pehle Sidebar mein API key daalein!")
