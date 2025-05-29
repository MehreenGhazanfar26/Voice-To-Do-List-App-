import streamlit as st
import sqlite3
import speech_recognition as sr

# === DATABASE SETUP ===
DB_NAME = "voice_todo.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create the table ONLY if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending'
        )
    """)
    
    conn.commit()
    conn.close()

# === DATABASE FUNCTIONS ===
def add_task(task):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status(task_id, status):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# === VOICE INPUT FUNCTION ===
def voice_input():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("🎤 Speak your task now...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("😕 Could not understand audio.")
    except sr.RequestError:
        st.error("⚠️ Could not connect to speech recognition service.")
    except Exception as e:
        st.error(f"🎤 Microphone error: {e}")
    return ""

# === INITIALIZE DATABASE ===
init_db()

# === STREAMLIT UI ===
st.title("🎙️ Voice To-Do List")
st.caption("Speak or type your tasks. Manage them with Done and Delete buttons.")

# === VOICE TASK ADDITION ===
if st.button("🎤 Speak to Add Task"):
    spoken_task = voice_input()
    if spoken_task:
        add_task(spoken_task)
        st.success(f"✅ Task added: {spoken_task}")
        st.rerun()

# === MANUAL TEXT TASK ENTRY ===
task_input = st.text_input("Add a new task (optional):")
if st.button("Add Task"):
    if task_input:
        add_task(task_input)
        st.success("✅ Task added successfully!")
        st.rerun()
    else:
        st.warning("⚠️ Please enter a task.")

# === DISPLAY TASKS ===
tasks = get_tasks()
if tasks:
    st.subheader("📋 Your Tasks:")
    for task in tasks:
        task_id, task_text, task_status = task
        col1, col2, col3 = st.columns([6, 2, 2])
        with col1:
            st.write(f"**{task_text}** ({task_status})")
        with col2:
            if task_status != "completed":
                if st.button("✅ Done", key=f"done_{task_id}"):
                    update_task_status(task_id, "completed")
                    st.rerun()
            else:
                st.success("✅ Done")
        with col3:
            if st.button("❌ Delete", key=f"delete_{task_id}"):
                delete_task(task_id)
                st.rerun()
else:
    st.info("No tasks added yet.")

