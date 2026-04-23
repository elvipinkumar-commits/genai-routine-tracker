import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE SETUP ---
# Database initialize karne ka function
def init_db():
    conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, 
                  task TEXT, 
                  category TEXT, 
                  status TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- APP CONFIG ---
st.set_page_config(page_title="Gen-AI Tracker", page_icon="🤖")

# --- SIDEBAR: PROGRESS TRACKING ---
st.sidebar.title("🚀 Gen-AI Roadmap")
roadmap_steps = [
    "Step 0: Python for AI",
    "Step 1: Gen AI Basics",
    "Step 2: Advanced AI (RAG/Agents)",
    "Step 3: Deployment & Fine-tuning"
]
selected_step = st.sidebar.selectbox("Current Stage:", roadmap_steps)

# Sidebar Progress Bar
progress_val = st.sidebar.slider("Step Completion (%)", 0, 100, 10)
st.sidebar.progress(progress_val)

# --- MAIN UI ---
st.title("📅 Daily Routine Tracker")
st.markdown(f"Goal: **{selected_step}** complete karna hai! 💪")

# Input Form
with st.container():
    st.subheader("Naya Task Add Karein")
    col1, col2 = st.columns([2, 1])
    with col1:
        task_input = st.text_input("Aaj ka topic (e.g. For Loops in Python)", placeholder="Yahan likhein...")
    with col2:
        date_input = st.date_input("Target Date", datetime.now())
    
    if st.button("Save Task"):
        if task_input:
            conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
            c = conn.cursor()
            c.execute("INSERT INTO tasks (date, task, category, status) VALUES (?, ?, ?, ?)",
                      (date_input.strftime("%Y-%m-%d"), task_input, selected_step, "Pending"))
            conn.commit()
            conn.close()
            st.success("Bahut badhiya! Task save ho gaya.")
        else:
            st.error("Pehle task ka naam toh likhiye!")

# --- DISPLAY DATA ---
st.divider()
st.subheader("📑 Aapka Learning Log")

conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
df = pd.read_sql_query("SELECT id, date, task, category, status FROM tasks ORDER BY date DESC", conn)
conn.close()

if not df.empty:
    # Task status update karne ka option
    st.dataframe(df, use_container_width=True)
    if st.button("Clear All History"):
        conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
        c = conn.cursor()
        c.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
        st.warning("Saara data delete ho gaya!")
        st.rerun()
else:
    st.info("Abhi tak koi task add nahi kiya gaya hai.")

# --- AI COACH TIP ---
st.divider()
st.subheader("🤖 AI Strategy Tip")
tips = {
    "Step 0: Python for AI": "💡 Tip: Rozana kam se kam 5 small programs banayein.",
    "Step 1: Gen AI Basics": "💡 Tip: Prompt Engineering ke techniques (Few-shot) ko practical try karein.",
    "Step 2: Advanced AI (RAG/Agents)": "💡 Tip: LangChain ya LlamaIndex ke documentation padhna shuru karein.",
    "Step 3: Deployment & Fine-tuning": "💡 Tip: Apni app ko share karke feedback lein."
}
st.info(tips[selected_step])