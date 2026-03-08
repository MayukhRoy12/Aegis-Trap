from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from google import genai
import json
import datetime
import os
import requests

# Initialize FastAPI
app = FastAPI()

# Your Gemini API Key
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")

# --- YOUR TELEGRAM KEYS ---
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" 
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# File to store our hacker logs
LOG_FILE = "honeypot_logs.json"

def get_geo_info(ip):
    """Translates an IP address into Latitude/Longitude."""
    # The Hackathon Trick: Faking local network attacks to show up in Kolkata
    if ip == "127.0.0.1" or ip.startswith("192.168."):
        return {"lat": 22.5726, "lon": 88.3639, "city": "Kolkata (Local Network)", "country": "India"}
    
    # Real public internet attack lookup
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,lat,lon"
        response = requests.get(url, timeout=2).json()
        if response.get("status") == "success":
            return {
                "lat": response["lat"], 
                "lon": response["lon"], 
                "city": response["city"], 
                "country": response["country"]
            }
    except Exception as e:
        print(f"Geo-IP Error: {e}")
        pass 
        
    return {"lat": None, "lon": None, "city": "Unknown", "country": "Unknown"}

def send_telegram_alert(ip, path, city):
    """Sends a live alert to your phone via Telegram."""
    if TELEGRAM_BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        return # Skip if keys aren't set yet
        
    message = f"🚨 *AEGIS-TRAP ALERT* 🚨\n\n🕵️ Attacker IP: `{ip}`\n📍 Location: {city}\n🎯 Target: `{path}`\n\n_Honeypot trap triggered!_"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception as e:
        print(f"Telegram Error: {e}")

def log_attack(ip, user_agent, path):
    """Saves the attacker's details and location to a JSON file."""
    geo_data = get_geo_info(ip)
    
    # 📱 FIRE THE TELEGRAM ALERT!
    send_telegram_alert(ip, path, geo_data["city"])
    
    log_entry = {
        "timestamp": str(datetime.datetime.now()),
        "ip_address": ip,
        "user_agent": user_agent,
        "path_attacked": path,
        "city": geo_data["city"],
        "country": geo_data["country"],
        "lat": geo_data["lat"],
        "lon": geo_data["lon"]
    }
    
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            try:
                logs = json.load(f)
            except:
                pass
                
    logs.append(log_entry)
    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

@app.get("/", response_class=HTMLResponse)
async def serve_homepage(request: Request):
    """Serves the fake camouflage homepage to humans."""
    
    # We still log the visit so it shows up on your Streamlit map!
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    log_attack(client_ip, user_agent, "/ (Homepage Visit)")

    # The fake HTML website
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Staff Portal - Maintenance</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; padding: 50px; background-color: #f4f4f9; }
            .container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }
            h1 { color: #2c3e50; }
            p { color: #555; line-height: 1.6;}
            .footer { margin-top: 30px; font-size: 12px; color: #aaa; }
            .btn { display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚙️ Portal Under Maintenance</h1>
            <p>The Staff & Faculty Intranet is currently undergoing scheduled security upgrades.</p>
            <p>Please check back later. If you require immediate administrative access, please use the secure admin login gateway.</p>
            <a href="#" class="btn">Contact IT Helpdesk</a>
            <div class="footer">
                &copy; 2026 Enterprise IT Services. All restricted areas strictly monitored.
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(request: Request, path: str):
    """This catches EVERY hidden request to the server (The Honeypot)."""
    
    # 🛑 Stop browser icons from wasting your API quota
    if path == "favicon.ico":
        return {"status": "ignored"}
    
    # 1. Log the attacker's details
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    log_attack(client_ip, user_agent, f"/{path}")

    # 2. Generate fake, juicy data using AI
    prompt = "Generate a highly realistic JSON object containing 3 fake but realistic user accounts with usernames, emails, and hashed passwords. Output ONLY valid JSON, nothing else."
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        # Clean up the response to ensure it's pure JSON
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        fake_data = json.loads(clean_json)
        
    except Exception as e:
        # Fallback just in case the AI API fails (like rate limits)
        print(f"AI Generation Error: {e}")
        fake_data = {
            "error": "Database connection timeout", 
            "fake_admin": "admin", 
            "fake_hash": "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
        }

    # 3. Serve the fake data to the attacker
    return fake_data