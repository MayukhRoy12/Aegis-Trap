import streamlit as st
import json
import pandas as pd
import os
import time
from google import genai

# Page config must be the first Streamlit command
st.set_page_config(page_title="Aegis-Trap Defender UI", layout="wide")

# --- CUSTOM CSS GLOW-UP ---
st.markdown("""
    <style>
    h1 { text-shadow: 0 0 10px #00FF41, 0 0 20px #00FF41; color: #00FF41 !important; }
    [data-testid="stMetricValue"] { color: #00FF41 !important; text-shadow: 0 0 5px #00FF41; }
    [data-testid="stDataFrame"] { border: 1px solid #00FF41; }
    </style>
""", unsafe_allow_html=True)

# Initialize Gemini AI
client = genai.Client(api_key="AIzaSyDYaUIL07IEId52BZxrGjG4oAT0wiI3IXM")

st.title("🛡️ Aegis-Trap: Live Threat Intelligence")
st.markdown("Real-time monitoring, geo-tracking, and automated threat scoring.")

# --- SIDEBAR CONTROLS ---
st.sidebar.title("⚙️ SOC Control Panel")
auto_refresh = st.sidebar.checkbox("🟢 Live Auto-Refresh", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 GenAI Threat Analyst")

# We use Session State so the AI report doesn't disappear when the page reloads!
if "ai_report" not in st.session_state:
    st.session_state.ai_report = None

LOG_FILE = "honeypot_logs.json"

def calculate_threat_level(score):
    if score >= 15: return "🔴 CRITICAL"
    elif score >= 5: return "🟠 ELEVATED"
    else: return "🟡 LOW"

# 1. Load and display all the data
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r") as f:
        try:
            logs = json.load(f)
            if logs:
                df = pd.DataFrame(logs)
                
                # --- TOP METRICS ---
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Attacks Blocked", len(logs))
                col2.metric("Unique IPs Logged", df['ip_address'].nunique())
                col3.metric("Most Targeted Path", df['path_attacked'].mode()[0])
                
                # --- 🧠 THREAT ACTOR ANALYTICS ---
                threat_df = df.groupby('ip_address').agg(
                    Total_Hits=('timestamp', 'count'),
                    Unique_Paths=('path_attacked', 'nunique'),
                    Location=('city', 'first')
                ).reset_index()

                threat_df['Danger_Score'] = (threat_df['Total_Hits'] * 1) + (threat_df['Unique_Paths'] * 2)
                threat_df['Risk_Level'] = threat_df['Danger_Score'].apply(calculate_threat_level)
                threat_df = threat_df.sort_values(by='Danger_Score', ascending=False)

                # --- NEW: FIREWALL AUTO-BAN LOGIC ---
                banned_ips = threat_df[threat_df['Danger_Score'] >= 15]
                monitored_ips = threat_df[threat_df['Danger_Score'] < 15]

                # --- THE AI BUTTON ACTION ---
                if st.sidebar.button("Generate Executive Briefing"):
                    with st.spinner("Aegis-AI is analyzing threat telemetry..."):
                        top_threats = threat_df.head(5).to_dict('records')
                        prompt = f"""
                        You are 'Aegis', an elite AI cybersecurity analyst. Review this live threat data:
                        {top_threats}
                        Write a highly professional, 2-paragraph executive briefing. 
                        Highlight the most dangerous IPs, their locations, and their danger score. 
                        Use a serious, urgent, but controlled tone. Do not use markdown tables.
                        """
                        try:
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=prompt
                            )
                            st.session_state.ai_report = response.text
                        except Exception as e:
                            st.session_state.ai_report = f"AI Error: {e}"

                # --- DISPLAY THE AI REPORT ---
                if st.session_state.ai_report:
                    st.subheader("🧠 Aegis AI Executive Briefing")
                    st.success(st.session_state.ai_report)

                # --- 🧱 DISPLAY FIREWALL QUARANTINE ---
                st.subheader("🧱 Active Firewall (Auto-Bans)")
                if not banned_ips.empty:
                    st.error(f"⚠️ {len(banned_ips)} IP(s) EXCEEDED CRITICAL THRESHOLD. NETWORK ACCESS REVOKED.")
                    st.dataframe(
                        banned_ips[['Risk_Level', 'ip_address', 'Location', 'Danger_Score']], 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.success("✅ Firewall Active: No IP addresses have exceeded the critical ban threshold yet.")

                # --- MAP CODE ---
                st.subheader("🌍 Live Threat Map")
                if 'lat' in df.columns and 'lon' in df.columns:
                    map_data = df.dropna(subset=['lat', 'lon'])
                    if not map_data.empty:
                        st.map(map_data[['lat', 'lon']])
                
                # --- DATA TABLES ---
                st.subheader("🕵️‍♂️ Active Threat Monitoring (Non-Banned)")
                if not monitored_ips.empty:
                    st.dataframe(
                        monitored_ips[['Risk_Level', 'ip_address', 'Location', 'Danger_Score', 'Total_Hits', 'Unique_Paths']], 
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No lower-level threats currently being monitored.")
                
                st.divider()
                col_chart, col_logs = st.columns([1, 2])
                with col_chart:
                    st.subheader("Target Distribution")
                    st.bar_chart(df['path_attacked'].value_counts())
                with col_logs:
                    st.subheader("🚨 Raw Event Logs")
                    display_cols = ['timestamp', 'ip_address', 'path_attacked']
                    available_cols = [col for col in display_cols if col in df.columns]
                    st.dataframe(df[available_cols], use_container_width=True, hide_index=True)
                    
            else:
                st.info("System Secure. Waiting for attackers...")
        except Exception as e:
             st.error(f"Error reading logs: {e}")
else:
    st.info("System Secure. Waiting for attackers...")

# 2. Smart Auto-Refresh!
if auto_refresh:
    time.sleep(3) 
    st.rerun()