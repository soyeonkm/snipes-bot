import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Slack app
app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET")
)

# --- Supabase setup ---
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_snipe_count(user_id):
    """Get snipe count for a user from Supabase."""
    try:
        response = supabase.table("snipes").select("count").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["count"]
        return 0
    except Exception as e:
        print(f"Error fetching snipe count for {user_id}: {e}")
        return 0

def increment_snipe_count(user_id, increment_by=1):
    """Increment snipe count for a user in Supabase."""
    try:
        current_count = get_snipe_count(user_id)
        new_count = current_count + increment_by
        
        # Upsert the record (insert or update)
        supabase.table("snipes").upsert({
            "user_id": user_id,
            "count": new_count
        }).execute()
        
        return new_count
    except Exception as e:
        print(f"Error updating snipe count for {user_id}: {e}")
        return current_count

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

    # Increment sender's snipe count in Supabase
    count = increment_snipe_count(sender_id, len(tagged_users))

    # Get sender's name from Slack
    sender_name = get_user_name(client, sender_id)

    # Send fun message
    if count == 1:
        say(f"Sniped! {sender_name} has {count} snipe!")
    else:
        say(f"Sniped! {sender_name} has {count} snipes!")

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
