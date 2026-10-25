import os
import sys
from datetime import date
from slack_sdk import WebClient
from supabase import create_client
from dotenv import load_dotenv

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

def fetch_top(supabase):
    """Top 5 snipers, highest count first."""
    return supabase.table("snipes").select("user_id, username, count").order("count", desc=True).limit(5).execute().data

def build_message(rows, subtitle=None):
    """Format leaderboard rows (ordered by count desc) as Slack message kwargs (text + blocks)."""
    body = "\n".join(
        f"{MEDALS.get(i, f'{i}.')} {row.get('username') or row['user_id']}: *{row['count']}* {'snipe' if row['count'] == 1 else 'snipes'}"
        for i, row in enumerate(rows, 1)
    ) or "Nothing yet! Start sniping people!"
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": "🎯 Snipes Leaderboard"}}]
    if subtitle:
        blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": subtitle}]})
    blocks += [{"type": "divider"}, {"type": "section", "text": {"type": "mrkdwn", "text": body}}]
    # text is the notification/fallback version of the blocks
    return {"text": "🏆 *Snipes Leaderboard*\n" + body, "blocks": blocks}

def send_summary():
    load_dotenv()
    channel = os.getenv("SLACK_CHANNEL_ID")
    if not channel:
        sys.exit("Error: SLACK_CHANNEL_ID must be set")

    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    today = date.today()
    WebClient(token=os.getenv("SLACK_BOT_TOKEN")).chat_postMessage(channel=channel, **build_message(fetch_top(supabase), f"Week of {today:%b} {today.day}"))
    print("Weekly summary posted.")

if __name__ == "__main__":
    send_summary()
