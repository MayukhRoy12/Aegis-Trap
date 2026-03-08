**Prerequisites**



pip install google-genai

pip install fastapi uvicorn google-generativeai streamlit

pip install requests







**API KEY :** https://aistudio.google.com/app/apikey











**main.py**



from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse

from google import genai

import json

import datetime

import os

import requests



\# Initialize FastAPI

app = FastAPI()



\# Your Gemini API Key

client = genai.Client(api\_key="AIzaSyDYaUIL07IEId52BZxrGjG4oAT0wiI3IXM")



\# --- YOUR TELEGRAM KEYS ---

TELEGRAM\_BOT\_TOKEN = "8715417188:AAEcxg9WeEQfEu-dFMEXLEz2aFTKmiE-NHA" 

TELEGRAM\_CHAT\_ID = "5624049823"



\# File to store our hacker logs

LOG\_FILE = "honeypot\_logs.json"



def get\_geo\_info(ip):

&nbsp;   """Translates an IP address into Latitude/Longitude."""

&nbsp;   # The Hackathon Trick: Faking local network attacks to show up in Kolkata

&nbsp;   if ip == "127.0.0.1" or ip.startswith("192.168."):

&nbsp;       return {"lat": 22.5726, "lon": 88.3639, "city": "Kolkata (Local Network)", "country": "India"}

&nbsp;   

&nbsp;   # Real public internet attack lookup

&nbsp;   try:

&nbsp;       url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"

&nbsp;       response = requests.get(url, timeout=2).json()

&nbsp;       if response.get("status") == "success":

&nbsp;           return {

&nbsp;               "lat": response\["lat"], 

&nbsp;               "lon": response\["lon"], 

&nbsp;               "city": response\["city"], 

&nbsp;               "country": response\["country"]

&nbsp;           }

&nbsp;   except Exception as e:

&nbsp;       print(f"Geo-IP Error: {e}")

&nbsp;       pass 

&nbsp;       

&nbsp;   return {"lat": None, "lon": None, "city": "Unknown", "country": "Unknown"}



def send\_telegram\_alert(ip, path, city):

&nbsp;   """Sends a live alert to your phone via Telegram."""

&nbsp;   if TELEGRAM\_BOT\_TOKEN == "PASTE\_YOUR\_BOT\_TOKEN\_HERE":

&nbsp;       return # Skip if keys aren't set yet

&nbsp;       

&nbsp;   message = f"🚨 \*AEGIS-TRAP ALERT\* 🚨\\n\\n🕵️ Attacker IP: `{ip}`\\n📍 Location: {city}\\n🎯 Target: `{path}`\\n\\n\_Honeypot trap triggered!\_"

&nbsp;   

&nbsp;   url = f"https://api.telegram.org/bot{TELEGRAM\_BOT\_TOKEN}/sendMessage"

&nbsp;   payload = {

&nbsp;       "chat\_id": TELEGRAM\_CHAT\_ID,

&nbsp;       "text": message,

&nbsp;       "parse\_mode": "Markdown"

&nbsp;   }

&nbsp;   try:

&nbsp;       requests.post(url, json=payload, timeout=3)

&nbsp;   except Exception as e:

&nbsp;       print(f"Telegram Error: {e}")



def log\_attack(ip, user\_agent, path):

&nbsp;   """Saves the attacker's details and location to a JSON file."""

&nbsp;   geo\_data = get\_geo\_info(ip)

&nbsp;   

&nbsp;   # 📱 FIRE THE TELEGRAM ALERT!

&nbsp;   send\_telegram\_alert(ip, path, geo\_data\["city"])

&nbsp;   

&nbsp;   log\_entry = {

&nbsp;       "timestamp": str(datetime.datetime.now()),

&nbsp;       "ip\_address": ip,

&nbsp;       "user\_agent": user\_agent,

&nbsp;       "path\_attacked": path,

&nbsp;       "city": geo\_data\["city"],

&nbsp;       "country": geo\_data\["country"],

&nbsp;       "lat": geo\_data\["lat"],

&nbsp;       "lon": geo\_data\["lon"]

&nbsp;   }

&nbsp;   

&nbsp;   logs = \[]

&nbsp;   if os.path.exists(LOG\_FILE):

&nbsp;       with open(LOG\_FILE, "r") as f:

&nbsp;           try:

&nbsp;               logs = json.load(f)

&nbsp;           except:

&nbsp;               pass

&nbsp;               

&nbsp;   logs.append(log\_entry)

&nbsp;   with open(LOG\_FILE, "w") as f:

&nbsp;       json.dump(logs, f, indent=4)



@app.get("/", response\_class=HTMLResponse)

async def serve\_homepage(request: Request):

&nbsp;   """Serves the fake camouflage homepage to humans."""

&nbsp;   

&nbsp;   # We still log the visit so it shows up on your Streamlit map!

&nbsp;   client\_ip = request.client.host

&nbsp;   user\_agent = request.headers.get("user-agent", "Unknown")

&nbsp;   log\_attack(client\_ip, user\_agent, "/ (Homepage Visit)")



&nbsp;   # The fake HTML website

&nbsp;   html\_content = """

&nbsp;   <!DOCTYPE html>

&nbsp;   <html>

&nbsp;   <head>

&nbsp;       <title>Staff Portal - Maintenance</title>

&nbsp;       <style>

&nbsp;           body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background-color: #f4f4f9; }

&nbsp;           .container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }

&nbsp;           h1 { color: #2c3e50; }

&nbsp;           p { color: #555; line-height: 1.6;}

&nbsp;           .footer { margin-top: 30px; font-size: 12px; color: #aaa; }

&nbsp;           .btn { display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; }

&nbsp;       </style>

&nbsp;   </head>

&nbsp;   <body>

&nbsp;       <div class="container">

&nbsp;           <h1>⚙️ Portal Under Maintenance</h1>

&nbsp;           <p>The Staff \& Faculty Intranet is currently undergoing scheduled security upgrades.</p>

&nbsp;           <p>Please check back later. If you require immediate administrative access, please use the secure admin login gateway.</p>

&nbsp;           <a href="#" class="btn">Contact IT Helpdesk</a>

&nbsp;           <div class="footer">

&nbsp;               \&copy; 2026 Enterprise IT Services. All restricted areas strictly monitored.

&nbsp;           </div>

&nbsp;       </div>

&nbsp;   </body>

&nbsp;   </html>

&nbsp;   """

&nbsp;   return html\_content



@app.api\_route("/{path:path}", methods=\["GET", "POST", "PUT", "DELETE"])

async def catch\_all(request: Request, path: str):

&nbsp;   """This catches EVERY hidden request to the server (The Honeypot)."""

&nbsp;   

&nbsp;   # 🛑 Stop browser icons from wasting your API quota

&nbsp;   if path == "favicon.ico":

&nbsp;       return {"status": "ignored"}

&nbsp;   

&nbsp;   # 1. Log the attacker's details

&nbsp;   client\_ip = request.client.host

&nbsp;   user\_agent = request.headers.get("user-agent", "Unknown")

&nbsp;   log\_attack(client\_ip, user\_agent, f"/{path}")



&nbsp;   # 2. Generate fake, juicy data using AI

&nbsp;   prompt = "Generate a highly realistic JSON object containing 3 fake but realistic user accounts with usernames, emails, and hashed passwords. Output ONLY valid JSON, nothing else."

&nbsp;   

&nbsp;   try:

&nbsp;       response = client.models.generate\_content(

&nbsp;           model='gemini-2.5-flash',

&nbsp;           contents=prompt

&nbsp;       )

&nbsp;       # Clean up the response to ensure it's pure JSON

&nbsp;       clean\_json = response.text.replace("```json", "").replace("```", "").strip()

&nbsp;       fake\_data = json.loads(clean\_json)

&nbsp;       

&nbsp;   except Exception as e:

&nbsp;       # Fallback just in case the AI API fails (like rate limits)

&nbsp;       print(f"AI Generation Error: {e}")

&nbsp;       fake\_data = {

&nbsp;           "error": "Database connection timeout", 

&nbsp;           "fake\_admin": "admin", 

&nbsp;           "fake\_hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"

&nbsp;       }



&nbsp;   # 3. Serve the fake data to the attacker

&nbsp;   return fake\_data









**dashboard.py**



import streamlit as st

import json

import pandas as pd

import os

import time

from google import genai



\# Page config must be the first Streamlit command

st.set\_page\_config(page\_title="Aegis-Trap Defender UI", layout="wide")



\# --- CUSTOM CSS GLOW-UP ---

st.markdown("""

&nbsp;   <style>

&nbsp;   h1 { text-shadow: 0 0 10px #00FF41, 0 0 20px #00FF41; color: #00FF41 !important; }

&nbsp;   \[data-testid="stMetricValue"] { color: #00FF41 !important; text-shadow: 0 0 5px #00FF41; }

&nbsp;   \[data-testid="stDataFrame"] { border: 1px solid #00FF41; }

&nbsp;   </style>

""", unsafe\_allow\_html=True)



\# Initialize Gemini AI

client = genai.Client(api\_key="AIzaSyDYaUIL07IEId52BZxrGjG4oAT0wiI3IXM")



st.title("🛡️ Aegis-Trap: Live Threat Intelligence")

st.markdown("Real-time monitoring, geo-tracking, and automated threat scoring.")



\# --- SIDEBAR CONTROLS ---

st.sidebar.title("⚙️ SOC Control Panel")

auto\_refresh = st.sidebar.checkbox("🟢 Live Auto-Refresh", value=True)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🤖 GenAI Threat Analyst")



\# We use Session State so the AI report doesn't disappear when the page reloads!

if "ai\_report" not in st.session\_state:

&nbsp;   st.session\_state.ai\_report = None



LOG\_FILE = "honeypot\_logs.json"



def calculate\_threat\_level(score):

&nbsp;   if score >= 15: return "🔴 CRITICAL"

&nbsp;   elif score >= 5: return "🟠 ELEVATED"

&nbsp;   else: return "🟡 LOW"



\# 1. Load and display all the data

if os.path.exists(LOG\_FILE):

&nbsp;   with open(LOG\_FILE, "r") as f:

&nbsp;       try:

&nbsp;           logs = json.load(f)

&nbsp;           if logs:

&nbsp;               df = pd.DataFrame(logs)

&nbsp;               

&nbsp;               # --- TOP METRICS ---

&nbsp;               col1, col2, col3 = st.columns(3)

&nbsp;               col1.metric("Total Attacks Blocked", len(logs))

&nbsp;               col2.metric("Unique IPs Logged", df\['ip\_address'].nunique())

&nbsp;               col3.metric("Most Targeted Path", df\['path\_attacked'].mode()\[0])

&nbsp;               

&nbsp;               # --- 🧠 THREAT ACTOR ANALYTICS ---

&nbsp;               threat\_df = df.groupby('ip\_address').agg(

&nbsp;                   Total\_Hits=('timestamp', 'count'),

&nbsp;                   Unique\_Paths=('path\_attacked', 'nunique'),

&nbsp;                   Location=('city', 'first')

&nbsp;               ).reset\_index()



&nbsp;               threat\_df\['Danger\_Score'] = (threat\_df\['Total\_Hits'] \* 1) + (threat\_df\['Unique\_Paths'] \* 2)

&nbsp;               threat\_df\['Risk\_Level'] = threat\_df\['Danger\_Score'].apply(calculate\_threat\_level)

&nbsp;               threat\_df = threat\_df.sort\_values(by='Danger\_Score', ascending=False)



&nbsp;               # --- NEW: FIREWALL AUTO-BAN LOGIC ---

&nbsp;               banned\_ips = threat\_df\[threat\_df\['Danger\_Score'] >= 15]

&nbsp;               monitored\_ips = threat\_df\[threat\_df\['Danger\_Score'] < 15]



&nbsp;               # --- THE AI BUTTON ACTION ---

&nbsp;               if st.sidebar.button("Generate Executive Briefing"):

&nbsp;                   with st.spinner("Aegis-AI is analyzing threat telemetry..."):

&nbsp;                       top\_threats = threat\_df.head(5).to\_dict('records')

&nbsp;                       prompt = f"""

&nbsp;                       You are 'Aegis', an elite AI cybersecurity analyst. Review this live threat data:

&nbsp;                       {top\_threats}

&nbsp;                       Write a highly professional, 2-paragraph executive briefing. 

&nbsp;                       Highlight the most dangerous IPs, their locations, and their danger score. 

&nbsp;                       Use a serious, urgent, but controlled tone. Do not use markdown tables.

&nbsp;                       """

&nbsp;                       try:

&nbsp;                           response = client.models.generate\_content(

&nbsp;                               model='gemini-2.5-flash',

&nbsp;                               contents=prompt

&nbsp;                           )

&nbsp;                           st.session\_state.ai\_report = response.text

&nbsp;                       except Exception as e:

&nbsp;                           st.session\_state.ai\_report = f"AI Error: {e}"



&nbsp;               # --- DISPLAY THE AI REPORT ---

&nbsp;               if st.session\_state.ai\_report:

&nbsp;                   st.subheader("🧠 Aegis AI Executive Briefing")

&nbsp;                   st.success(st.session\_state.ai\_report)



&nbsp;               # --- 🧱 DISPLAY FIREWALL QUARANTINE ---

&nbsp;               st.subheader("🧱 Active Firewall (Auto-Bans)")

&nbsp;               if not banned\_ips.empty:

&nbsp;                   st.error(f"⚠️ {len(banned\_ips)} IP(s) EXCEEDED CRITICAL THRESHOLD. NETWORK ACCESS REVOKED.")

&nbsp;                   st.dataframe(

&nbsp;                       banned\_ips\[\['Risk\_Level', 'ip\_address', 'Location', 'Danger\_Score']], 

&nbsp;                       use\_container\_width=True,

&nbsp;                       hide\_index=True

&nbsp;                   )

&nbsp;               else:

&nbsp;                   st.success("✅ Firewall Active: No IP addresses have exceeded the critical ban threshold yet.")



&nbsp;               # --- MAP CODE ---

&nbsp;               st.subheader("🌍 Live Threat Map")

&nbsp;               if 'lat' in df.columns and 'lon' in df.columns:

&nbsp;                   map\_data = df.dropna(subset=\['lat', 'lon'])

&nbsp;                   if not map\_data.empty:

&nbsp;                       st.map(map\_data\[\['lat', 'lon']])

&nbsp;               

&nbsp;               # --- DATA TABLES ---

&nbsp;               st.subheader("🕵️‍♂️ Active Threat Monitoring (Non-Banned)")

&nbsp;               if not monitored\_ips.empty:

&nbsp;                   st.dataframe(

&nbsp;                       monitored\_ips\[\['Risk\_Level', 'ip\_address', 'Location', 'Danger\_Score', 'Total\_Hits', 'Unique\_Paths']], 

&nbsp;                       use\_container\_width=True,

&nbsp;                       hide\_index=True

&nbsp;                   )

&nbsp;               else:

&nbsp;                   st.info("No lower-level threats currently being monitored.")

&nbsp;               

&nbsp;               st.divider()

&nbsp;               col\_chart, col\_logs = st.columns(\[1, 2])

&nbsp;               with col\_chart:

&nbsp;                   st.subheader("Target Distribution")

&nbsp;                   st.bar\_chart(df\['path\_attacked'].value\_counts())

&nbsp;               with col\_logs:

&nbsp;                   st.subheader("🚨 Raw Event Logs")

&nbsp;                   display\_cols = \['timestamp', 'ip\_address', 'path\_attacked']

&nbsp;                   available\_cols = \[col for col in display\_cols if col in df.columns]

&nbsp;                   st.dataframe(df\[available\_cols], use\_container\_width=True, hide\_index=True)

&nbsp;                   

&nbsp;           else:

&nbsp;               st.info("System Secure. Waiting for attackers...")

&nbsp;       except Exception as e:

&nbsp;            st.error(f"Error reading logs: {e}")

else:

&nbsp;   st.info("System Secure. Waiting for attackers...")



\# 2. Smart Auto-Refresh!

if auto\_refresh:

&nbsp;   time.sleep(3) 

&nbsp;   st.rerun()











**Terminal 1**

uvicorn main:app --reload --port 8000







**Terminal 2**

streamlit run dashboard.py







**To see random passwords**

http://localhost:8000/test\_hack

http://127.0.0.1:8000/

http://127.0.0.1:8000/admin/db\_passwords



Open your web browser and trigger the trap a few times by going to your local server:



Go to http://127.0.0.1:8000/admin (Hit refresh 3 times)



Go to http://127.0.0.1:8000/.env (Hit refresh 1 time)



Go to http://127.0.0.1:8000/database\_backup (Hit refresh 2 times)





**For other computer**



In terminal 1, ctrl+c then uvicorn main:app --host 0.0.0.0 --port 8000


http://YOUR\_IPV4\_ADDRESS:8000/test\_hack      (like http://192.168.29.13:8000/test\_hack)



Turn Windows Defender Firewall on or off(if reqd)













**Telegram**



1. Search @BotFather
2. /start
3. /newbot
4. name - Aegis Trap Alerts
5. username - MayukhAegisBot
6. HTTP API:8715417188:AAEcxg9WeEQfEu-dFMEXLEz2aFTKmiE-NHA      - copy token
7. search in telegram @MayukhAegisBot    -     start
8. hello or Wake up!
9. https://api.telegram.org/bot<YOUR\_TOKEN>/getUpdates
10. You will see a block of text. Look for the number right after "chat":{"id":. It will be a string of numbers like 987654321. Copy this number!
11. \# --- YOUR TELEGRAM KEYS ---
12. TELEGRAM\_BOT\_TOKEN = "8715417188:AAEcxg9WeEQfEu-dFMEXLEz2aFTKmiE-NHA" 
13. TELEGRAM\_CHAT\_ID = "5624049823"......add these in main.py



**To test**



http://127.0.0.1:8000/admin/db\_passwords











**Create the Config File**



1. create folder ".streamlit"
2. inside this folder create text file "config.toml"



**paste** **in config.toml**



\[theme]

\# The glowing hacker green for buttons and highlights

primaryColor = "#00FF41"



\# Deep, dark terminal background

backgroundColor = "#0D1117"



\# Slightly lighter dark grey for the sidebar and data tables

secondaryBackgroundColor = "#161B22"



\# Classic terminal green for all the text

textColor = "#00FF41"



\# Forces the entire app to use a monospaced coding font

font = "monospace"



















**UEM Wifi**



Getting your local Wi-Fi IP is super easy, but there is actually a \*\*crucial Hackathon Trap\*\* hidden in university Wi-Fi networks that we need to prepare for right now!



Since you are using Windows, finding your IP takes about three seconds. Here is exactly what you will do the moment you connect to the UEM Wi-Fi on Friday:



\### 🔍 Step 1: Find the IP Address



1\. Open a new Terminal window (in VS Code or standard Command Prompt).

2\. Type this command and press Enter:

```cmd

ipconfig



```





3\. A bunch of text will pop up. Look for the section titled \*\*Wireless LAN adapter Wi-Fi\*\*.

4\. Look for the line that says \*\*IPv4 Address\*\*.

5\. The sequence of numbers next to it (e.g., `192.168.1.45` or `10.5.22.14`) is your new local IP!



\### ⚠️ Step 2: The University Wi-Fi Map Trap (Important!)



Remember how we wrote a trick into `main.py` so the Threat Map would show Kolkata when you tested it at home? We coded it to look for IPs starting with `192.168.` (which is what home Wi-Fi routers use).



However, massive university networks like UEM often use enterprise IP ranges that start with \*\*`10.`\*\* or \*\*`172.`\*\*. If UEM uses one of those, your map will suddenly go blank during the demo!



When you get your IP on Friday using `ipconfig`, check the first number. If it doesn't start with `192`, just make a 5-second edit to line 20 in your `main.py` file to include it:



\*\*Change this:\*\*

`if ip == "127.0.0.1" or ip.startswith("192.168."):`



\*\*To this (if your UEM IP starts with 10):\*\*

`if ip == "127.0.0.1" or ip.startswith("192.168.") or ip.startswith("10."):`



\### 🚀 Step 3: Start the Server for the Network



Earlier, we took off the `--host 0.0.0.0` command to fix your tunnel bug. To let the judges (or your friend's laptop) reach your server over the UEM Wi-Fi, you \*\*must\*\* put it back when you launch your server on Friday.



Run your FastAPI server in Terminal 1 exactly like this:



```bash

uvicorn main:app --host 0.0.0.0 --port 8000



```



Now, anyone else connected to the UEM Wi-Fi can type `http://<YOUR\_NEW\_IP>:8000/admin` into their own phone or laptop browser, and they will trigger your honeypot perfectly!



You have the code, you have the presentation script, and now you have the networking locked down. Shall we draft out the bullet points for those 5 presentation slides so your slide deck looks as professional as your dashboard?



































**What to show?**



1\. \*\*Clear the Logs:\*\* Delete your `honeypot\_logs.json` file. You want your Streamlit dashboard to say \*"System Secure. Waiting for attackers..."\* when the judges first see it.

2\. \*\*Open Three Tabs:\*\* \* Tab 1: The Camouflage Homepage (`http://127.0.0.1:8000/`)

\* Tab 2: The Streamlit Dashboard (`http://localhost:8501`)

\* Tab 3: Keep a duplicate of Tab 1 open and ready to type the "hack" URL.





3\. \*\*Phone Ready:\*\* Have your phone screen on, volume up (or vibrate on), with the Telegram app open or visible on your lock screen.



---



\### 🎭 Phase 1: The Hook (The Setup)



\*\*You (To the Judges):\*\* "Welcome to Aegis-Trap. Traditional firewalls try to keep hackers out. We take a different approach: we invite them in, trap them in a maze of AI-generated fake data, and track their every move. Let me show you."



\*👉 Point to Tab 1 (The Maintenance Page).\*

\*\*You:\*\* "To a human employee, our server looks like a standard, boring IT portal undergoing maintenance. But to an automated bot scanning for vulnerabilities, it’s a goldmine."



\### 🦹‍♂️ Phase 2: The Breach (The Trap)



\*\*You:\*\* "I am now going to play the role of the hacker. I run a script that searches for hidden database files."



\*👉 Switch to Tab 3. Type in `http://127.0.0.1:8000/admin/db\_passwords` and hit Enter.\*

\*\*You:\*\* "The hacker thinks they just scored! They see valid JSON with emails and hashed passwords. But this data is completely synthetic, generated on the fly by Gemini 2.5."



\### 🚨 Phase 3: The Alarm (Telegram)



\*👉 Grab your phone and show it to the judges.\*

\*\*You:\*\* "The second the hacker touched that fake file, our system triggered. I instantly received a Telegram alert with the attacker's IP, their location, and the exact file they tried to steal. Our Security Operations Center is now awake."



\### 🌍 Phase 4: The Analytics (Streamlit)



\*👉 Switch to Tab 2 (The Dashboard).\*

\*\*You:\*\* "This is our live SOC dashboard. As you can see, the attacker's IP has been logged. Because we use Geo-IP tracking, they are instantly plotted on our live Threat Map right here in Kolkata."



\### 🧱 Phase 5: The Escalation (Auto-Ban)



\*\*You:\*\* "Right now, they are in our 'Active Monitoring' zone with a low Danger Score. But what happens if it's a brute-force bot that won't stop scanning?"



\*👉 Go back to Tab 3 and spam the Refresh button rapidly 5 or 6 times.\*

\*👉 Switch back to Tab 2.\*

\*\*You:\*\* "Our algorithmic profiling engine detects the aggressive behavior. Watch the Danger Score climb. Once it hits 15... \*\[wait a second for the dashboard to refresh]\* ...the system automatically rips their IP out of the monitoring queue and throws them into the Active Firewall blocklist. Their access is revoked."



\### 🧠 Phase 6: The Grand Finale (GenAI Briefing)



\*\*You:\*\* "Normally, a security analyst would now have to spend an hour writing an incident report. With Aegis-Trap, we do it in three seconds."



\*👉 Click the "Generate Executive Briefing" button on the sidebar.\*

\*\*You:\*\* "We feed the live telemetry data directly into our Gemini AI model. It instantly generates a professional, ready-to-send executive summary of the exact attack that just occurred, detailing the threat level and the actions taken."



\*\*You:\*\* "That is Aegis-Trap. Active deception, real-time analytics, and automated defense. We'd love to answer any questions."



