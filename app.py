import streamlit as st
import pandas as pd
import random
import time
import io
from datetime import datetime

# --- CONFIGURATION ---
EXCEL_FILE = "ai_activity_log.xlsx"
TOTAL_STUDENTS = 62

# --- UI SETUP ---
st.set_page_config(page_title="AI Spotlight Arena", layout="wide")

# --- INITIALIZE SESSION STATES ---
if 'used_rolls' not in st.session_state:
    st.session_state.used_rolls = []
if 'current_student' not in st.session_state:
    st.session_state.current_student = None
if 'final_duration' not in st.session_state:
    st.session_state.final_duration = "0m 0s"

# --- SIDEBAR: SETTINGS & STATS ---
with st.sidebar:
    st.header("⚙️ Settings")
    dark_mode = st.toggle("🌙 Dark Mode", value=True)
    
    st.divider()
    
    st.subheader("📥 Export Data")
    try:
        df_for_download = pd.read_excel(EXCEL_FILE)
        csv = df_for_download.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📄 Download Report (CSV)",
            data=csv,
            file_name=f"AI_Activity_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    except:
        st.info("No data available to download yet.")

    st.divider()
    
    st.subheader("🧹 Session Control")
    if st.button("🔄 Reset All Roll Numbers"):
        st.session_state.used_rolls = []
        st.session_state.current_student = None
        st.session_state.final_duration = "0m 0s"
        st.toast("Memory cleared!")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    st.header("📊 Session Summary")
    try:
        current_df = pd.read_excel(EXCEL_FILE)
        p_count = len(current_df[current_df['Status'] == 'Present'])
        a_count = len(current_df[current_df['Status'] == 'Absent'])
        st.metric("Present ✅", p_count)
        st.metric("Absent ❌", a_count)
        if TOTAL_STUDENTS > 0:
            st.progress(p_count / TOTAL_STUDENTS)
    except:
        st.info("No records yet.")

# --- THE "FORCE TEXT VISIBILITY" CSS ---
# This section targets the exact HTML structure of Streamlit buttons
if dark_mode:
    bg_color = "#0E1117"
    text_color = "#FFFFFF"
    sidebar_bg = "#262730"
    btn_bg = "#31333F"
else:
    bg_color = "#FFFFFF"
    text_color = "#1A1C24"
    sidebar_bg = "#F0F2F6"
    btn_bg = "#1A1C24"  # Dark button for light mode

st.markdown(f"""
    <style>
    /* 1. Main App Background */
    .stApp {{ background-color: {bg_color}; }}
    
    /* 2. Global Text Color */
    h1, h2, h3, p, span, label, div[data-testid="stMarkdownContainer"] p {{ 
        color: {text_color} !important; 
    }}

    /* 3. Sidebar Contrast Fix */
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; }}
    [data-testid="stSidebar"] * {{ color: {text_color} !important; }}

    /* 4. THE BUTTON FIX: Targets the button and the hidden label containers */
    button {{
        background-color: {btn_bg} !important;
        border: 2px solid {text_color} !important;
        border-radius: 8px !important;
    }}

    /* This targets the specific text-container inside the button */
    button [data-testid="stMarkdownContainer"] p, 
    button div div div, 
    button span,
    button p {{
        color: white !important; /* Force white text on the dark button */
        font-weight: bold !important;
        font-size: 1rem !important;
        opacity: 1 !important;
    }}

    /* 5. Metrics visibility */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{ 
        color: {text_color} !important; 
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SAFE SAVE FUNCTION ---
def save_to_excel(data):
    try:
        try:
            df = pd.read_excel(EXCEL_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["Day", "Date", "Time", "Roll Number", "Status", "Topic", "Duration", "Content Star", "Delivery Star", "Total Score"])
        
        new_df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        new_df.to_excel(EXCEL_FILE, index=False)
        return True
    except PermissionError:
        st.error("⚠️ CLOSE EXCEL: Please close the file so I can save!")
        return False

# --- MAIN AREA ---
st.title("🤖 AI Spotlight: 5-Minute Pitch")

if st.button("🎡 CLICK TO SPIN THE WHEEL", use_container_width=True):
    available = [r for r in range(1, TOTAL_STUDENTS + 1) if r not in st.session_state.used_rolls]
    if available:
        placeholder = st.empty() 
        for _ in range(12):
            temp = random.choice(available)
            placeholder.markdown(f"<h1 style='text-align: center; color: {text_color};'>🎡 {temp}</h1>", unsafe_allow_html=True)
            time.sleep(0.06)
        
        selected = random.choice(available)
        st.session_state.current_student = selected
        st.session_state.used_rolls.append(selected)
        placeholder.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>🏆 ROLL {selected}</h1>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.warning("All students have participated!")

if st.session_state.current_student:
    st.divider()
    st.subheader(f"🎯 Candidate: Roll No. {st.session_state.current_student}")
    
    topic = st.text_input("AI Tool / Topic Name:", placeholder="What are they presenting?")

    st.write("### ⏱️ Live Stopwatch")
    stopwatch_display = st.empty()
    stopwatch_display.markdown(f"## ⏳ Time: 00:00")

    col1, col2 = st.columns(2)
    
    if col1.button("▶️ Start Timer", use_container_width=True):
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            mins, secs = divmod(int(elapsed), 60)
            st.session_state.final_duration = f"{mins}m {secs}s"
            stopwatch_display.markdown(f"## ⏳ Time: {mins:02d}:{secs:02d}")
            time.sleep(1)

    if col2.button("⏹️ Stop Timer", use_container_width=True):
        st.success(f"Final Time Captured: {st.session_state.final_duration}")

    st.subheader("⭐ Faculty Review")
    c1, c2 = st.columns(2)
    content = c1.select_slider("Content Quality", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐")
    delivery = c2.select_slider("Conveying Manner", options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"], value="⭐⭐⭐")

    save_col1, save_col2 = st.columns(2)
    
    if save_col1.button("💾 Save Present & Complete", use_container_width=True):
        now = datetime.now()
        entry = {
            "Day": now.strftime("%A"), "Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%I:%M %p"),
            "Roll Number": st.session_state.current_student, "Status": "Present", "Topic": topic,
            "Duration": st.session_state.final_duration, 
            "Content Star": len(content), "Delivery Star": len(delivery), 
            "Total Score": len(content) + len(delivery)
        }
        if save_to_excel(entry):
            st.session_state.current_student = None
            st.session_state.final_duration = "0m 0s"
            st.rerun()

    if save_col2.button("❌ Mark Absent", use_container_width=True):
        now = datetime.now()
        entry = {
            "Day": now.strftime("%A"), "Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%I:%M %p"),
            "Roll Number": st.session_state.current_student, "Status": "Absent", "Topic": "N/A",
            "Duration": "0m 0s", "Content Star": 0, "Delivery Star": 0, "Total Score": 0
        }
        if save_to_excel(entry):
            st.session_state.current_student = None
            st.rerun()