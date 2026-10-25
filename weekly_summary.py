import os
import sys
from slack_sdk import WebClient
from supabase import create_client
from dotenv import load_dotenv

MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
PAD = "\u2002"  # en space, nudges "4." / "5." right to line up with the medal emojis

def fetch_top(supabase):
    """Top 5 snipers, highest count first; ties go to whoever reached the count first."""
    return supabase.table("snipes").select("user_id, username, count").order("count", desc=True).order("updated_at").limit(5).execute().data

def build_message(rows):
    """Format leaderboard rows (ordered by count desc) as Slack message kwargs (text + blocks)."""
    body = "\n".join(
        f"{MEDALS.get(i, f'{PAD}{i}.')} {row.get('username') or row['user_id']}: *{row['count']}* {'snipe' if row['count'] == 1 else 'snipes'}"
        for i, row in enumerate(rows, 1)
    ) or "Nothing yet! Start sniping people!"
    blocks = [{"type": "header", "text": {"type": "plain_text", "text": "🏆 Snipes Leaderboard"}}]
    blocks += [{"type": "divider"}, {"type": "section", "text": {"type": "mrkdwn", "text": body}}]
    # text is the notification/fallback version of the blocks
    return {"text": "🏆 *Snipes Leaderboard*\n" + body, "blocks": blocks}

def send_summary():
    load_dotenv()
    channel = os.getenv("SLACK_CHANNEL_ID")
    if not channel:
        sys.exit("Error: SLACK_CHANNEL_ID must be set")

    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    WebClient(token=os.getenv("SLACK_BOT_TOKEN")).chat_postMessage(channel=channel, **build_message(fetch_top(supabase)))
    print("Weekly summary posted.")

if __name__ == "__main__":
    send_summary()
