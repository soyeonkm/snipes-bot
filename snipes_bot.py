from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import re
import json
import os

load_dotenv()

# -------------------------------
# Load or create counter storage
# -------------------------------
COUNTER_FILE = "tag_counts.json"

def load_counts():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_counts(counts):
    with open(COUNTER_FILE, "w") as f:
        json.dump(counts, f, indent=2)

counts = load_counts()

# -------------------------------
# Initialize the Slack app
# -------------------------------
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.event("message")
def handle_mentions(event, say):
    user = event.get("user")
    text = event.get("text", "")

    # Ignore bot messages or messages without a sender
    if not user or "bot_id" in event:
        return

    # Detect mentions like <@U12345>
    mentions = re.findall(r"<@([A-Z0-9]+)>", text)
    if mentions:
        counts[user] = counts.get(user, 0) + len(mentions)
        save_counts(counts)
        print(f"User {user} now has {counts[user]} tags!")

@app.command("/tagcount")
def tagcount(ack, respond):
    ack()
    leaderboard = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    if not leaderboard:
        respond("No tags yet!")
        return
    msg = "\n".join([f"<@{u}>: {c}" for u, c in leaderboard])
    respond(f"🏆 *Tag Leaderboard:*\n{msg}")

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
