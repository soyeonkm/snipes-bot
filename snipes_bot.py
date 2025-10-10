import os
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# --- JSON persistence setup ---
DATA_FILE = "snipes_data.json"

def load_snipes():
    """Load snipe counts from JSON file."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_snipes():
    """Save snipe counts to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(snipes_count, f, indent=2)

snipes_count = load_snipes()

# --- Helper functions ---
def get_user_name(client, user_id):
    """Fetch user's display name from Slack API."""
    try:
        response = client.users_info(user=user_id)
        return response["user"]["real_name"]
    except Exception as e:
        print(f"Error fetching user name for {user_id}: {e}")
        return user_id

# --- Message handler ---
@app.event("message")
def handle_message(event, say, client, logger):
    # Ignore messages from bots
    if event.get("subtype") == "bot_message":
        return
    
    text = event.get("text", "")
    sender_id = event.get("user")

    if not text or not sender_id:
        return

    # Find all mentions like <@U123ABC>
    tagged_users = re.findall(r"<@([A-Z0-9]+)>", text)
    if not tagged_users:
        return  # No one tagged → no snipes

    # Increment sender's snipe count
    snipes_count[sender_id] = snipes_count.get(sender_id, 0) + len(tagged_users)
    save_snipes()  # persist the updated data

    # Get sender’s name from Slack
    sender_name = get_user_name(client, sender_id)
    count = snipes_count[sender_id]

    # Send fun message
    say(f"🎯 {sender_name} has {count} snipes!")

    logger.info(f"{sender_name} sniped {len(tagged_users)} people. Total: {count}")

# --- Dummy HTTP server (keeps app alive on Render) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
