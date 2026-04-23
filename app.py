import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- DATABASE SETUP ---
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

# Function to update task status
# Hinglish: Ye function task ko 'Completed' mark karne ke liye hai
def complete_task(task_id):
    conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = 'Completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# --- APP CONFIG ---
st.set_page_config(page_title="Gen-AI Tracker Pro", page_icon="✅")

# --- SIDEBAR ---
st.sidebar.title("🚀 Roadmap Progress")
roadmap_steps = ["Step 0: Python", "Step 1: Basics", "Step 2: RAG/Agents", "Step 3: Deploy"]
selected_step = st.sidebar.selectbox("Current Stage:", roadmap_steps)
progress_val = st.sidebar.slider("Step Completion (%)", 0, 100, 20)
st.sidebar.progress(progress_val)

# --- MAIN UI ---
st.title("📅 Smart Routine Tracker")

# Form to add tasks
with st.expander("➕ Naya Task Add Karein", expanded=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        task_input = st.text_input("Topic Name")
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
            st.success("Task saved!")
            st.rerun()

# --- DISPLAY & COMPLETE TASKS ---
st.subheader("📑 Aapka Learning Log")

conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
df = pd.read_sql_query("SELECT * FROM tasks WHERE status = 'Pending' ORDER BY date ASC", conn)
done_df = pd.read_sql_query("SELECT * FROM tasks WHERE status = 'Completed' ORDER BY date DESC", conn)
conn.close()

# Display Pending Tasks with 'Done' Button
if not df.empty:
    for index, row in df.iterrows():
        col_t, col_b = st.columns([4, 1])
        with col_t:
            st.write(f"**{row['task']}** ({row['date']}) - *{row['category']}*")
        with col_b:
            if st.button("Done ✅", key=f"btn_{row['id']}"):
                complete_task(row['id'])
                st.toast(f"Shabaash! {row['task']} pura hua! 🎉")
                st.rerun()
else:
    st.info("Koi Pending task nahi hai. Chill karein ya naya add karein!")

# Show Completed Tasks
if not done_df.empty:
    with st.expander("✅ Completed Tasks (History)"):
        st.table(done_df[['date', 'task', 'category']])

# --- FOOTER ---
st.divider()
if st.button("Clear All Data"):
    conn = sqlite3.connect('routine_tracker.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM tasks")
    conn.commit()
    conn.close()
    st.rerun()
