import os
import sys
from slack_sdk import WebClient
from supabase import create_client
from dotenv import load_dotenv

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

def fetch_top(supabase):
    """Top 10 snipers, highest count first."""
    return supabase.table("snipes").select("user_id, username, count").order("count", desc=True).limit(10).execute().data

def build_message(rows):
    """Format leaderboard rows (ordered by count desc) as a Slack message."""
    if not rows:
        return "🎯 *Snipes Leaderboard*\nNothing yet! Start sniping people!"
    lines = [
        f"{MEDALS.get(i, f'{i}.')} {row.get('username') or row['user_id']}: *{row['count']}* {'snipe' if row['count'] == 1 else 'snipes'}"
        for i, row in enumerate(rows, 1)
    ]
    return "🎯 *Snipes Leaderboard*\n" + "\n".join(lines)

def send_summary():
    load_dotenv()
    channel = os.getenv("SLACK_CHANNEL_ID")
    if not channel:
        sys.exit("Error: SLACK_CHANNEL_ID must be set")

    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    WebClient(token=os.getenv("SLACK_BOT_TOKEN")).chat_postMessage(channel=channel, text=build_message(fetch_top(supabase)))
    print("Weekly summary posted.")

if __name__ == "__main__":
    send_summary()
