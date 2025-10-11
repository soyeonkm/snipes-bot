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

# --- HTTP server with leaderboard ---
class LeaderboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_leaderboard()
        elif self.path == '/health':
            self.serve_health()
        else:
            self.send_error(404)
    
    def serve_health(self):
        """Simple health check endpoint."""
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def serve_leaderboard(self):
        """Serve the snipes leaderboard as HTML."""
        try:
            # Fetch all snipes from Supabase, ordered by count
            response = supabase.table("snipes").select("*").order("count", desc=True).limit(50).execute()
            
            if not response.data:
                html = self.generate_html([], "Nothing yet! Start sniping people!")
            else:
                # Get user names from Slack
                leaderboard_data = []
                for entry in response.data:
                    user_id = entry['user_id']
                    count = entry['count']
                    # Try to get user name, fallback to user_id if it fails
                    try:
                        user_info = app.client.users_info(user=user_id)
                        user_name = user_info["user"]["real_name"] or user_info["user"]["name"]
                    except:
                        user_name = user_id
                    
                    leaderboard_data.append({
                        'name': user_name,
                        'count': count,
                        'user_id': user_id
                    })
                
                html = self.generate_html(leaderboard_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        
        except Exception as e:
            print(f"Error generating leaderboard: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = self.generate_html([], f"Error loading leaderboard: {str(e)}")
            self.wfile.write(error_html.encode('utf-8'))
    
    def generate_html(self, leaderboard_data, error_message=None):
        """Generate HTML for the leaderboard."""
        rows = ""
        if error_message:
            rows = f'<tr><td colspan="3" style="text-align: center; color: #666;">{error_message}</td></tr>'
        else:
            for idx, entry in enumerate(leaderboard_data, 1):
                medal = ""
                if idx == 1:
                    medal = "🥇"
                elif idx == 2:
                    medal = "🥈"
                elif idx == 3:
                    medal = "🥉"
                
                rows += f'''
                <tr>
                    <td>{medal} {idx}</td>
                    <td>{entry['name']}</td>
                    <td><strong>{entry['count']}</strong></td>
                </tr>
                '''
        
        html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Snipes Leaderboard</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: #f5f5f5;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    max-width: 800px;
                    width: 100%;
                    overflow: hidden;
                }}
                .header {{
                    background: #ffffff;
                    color: #333;
                    padding: 30px 30px 20px;
                    text-align: center;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .header h1 {{
                    font-size: 2em;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                .header p {{
                    font-size: 1em;
                    color: #666;
                }}
                .leaderboard {{
                    padding: 30px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th {{
                    background: #fafafa;
                    padding: 12px 15px;
                    text-align: left;
                    font-weight: 600;
                    color: #333;
                    border-bottom: 2px solid #e0e0e0;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                td {{
                    padding: 12px 15px;
                    border-bottom: 1px solid #f0f0f0;
                    color: #333;
                }}
                tr:hover {{
                    background: #fafafa;
                }}
                tr:last-child td {{
                    border-bottom: none;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9em;
                    border-top: 1px solid #e0e0e0;
                    background: #fafafa;
                }}
                @media (max-width: 600px) {{
                    .header h1 {{
                        font-size: 1.5em;
                    }}
                    td, th {{
                        padding: 10px;
                        font-size: 0.9em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 MKoBi Snipes Leaderboard</h1>
                </div>
                <div class="leaderboard">
                    <table>
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Name</th>
                                <th>Snipes</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        '''
        return html
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), LeaderboardHandler)
    print(f"Leaderboard server running on port {port}")
    server.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
