import os
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

def send_heartbeat():
    """Send a heartbeat ping to the Supabase database to keep the connection active."""
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
        return
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        
        # Insert a heartbeat record
        # We explicitly set created_at to avoid sending an empty dictionary,
        # although the database has a default 'now()' value.
        current_time = datetime.now(timezone.utc).isoformat()
        response = supabase.table("heartbeats").insert({
            "created_at": current_time
        }).execute()
        
        print(f"[{current_time}] Heartbeat sent successfully.")
        
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Error sending heartbeat: {e}")

if __name__ == "__main__":
    send_heartbeat()
