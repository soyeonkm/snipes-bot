# 🎯 Snipes Bot

A fun Slack bot that tracks "snipes" - whenever someone tags another user in a message! Includes a beautiful public leaderboard website.

## Features

- 🤖 **Slack Bot** - Automatically counts when users tag others
- 🏆 **Live Leaderboard** - Beautiful web interface showing top snipers
- 💾 **Persistent Storage** - Uses Supabase for reliable data storage
- 🚀 **Cloud-Ready** - Deploys easily to Northflank or any container platform
- 📱 **Responsive Design** - Leaderboard works perfectly on mobile

## How It Works

1. Someone tags a user in Slack **with a photo attached**: `Hey @john, check this out! 📸`
2. Bot responds with their current snipe count: `Sniped! Alice has 5 snipes!`
3. Leaderboard updates automatically showing the rankings

**Note**: A snipe only counts if the message includes both a user tag AND an image attachment!

## Quick Preview

### Slack Bot in Action

```
You: "Hey @alice @bob, look at this!" [with photo attached]
Bot: "Sniped! You have 3 snipes!"
```

### Leaderboard Website

- 🥇 Top users get medals (gold, silver, bronze)
- Real names from Slack
- Live data from Supabase
- Clean, modern design with purple gradient

## Setup

See **[QUICKSTART.md](QUICKSTART.md)** for setup instructions.

### Prerequisites

- Slack workspace with admin access
- Supabase account (free tier works great)
- Northflank account (or any hosting platform)

### Installation Steps

1. Create Supabase database table
2. Configure Slack app with Socket Mode
3. Set environment variables
4. Deploy to Northflank
5. (Optional) Set up the heartbeat Cron Job to keep free Supabase projects awake
6. Share leaderboard URL with team!

## Tech Stack

- **Python 3.11** - Core application
- **Slack Bolt SDK** - Slack integration with Socket Mode
- **Supabase** - PostgreSQL database backend
- **Northflank** - Container hosting platform

## Environment Variables

| Variable               | Description                           |
| ---------------------- | ------------------------------------- |
| `SLACK_BOT_TOKEN`      | Bot OAuth token from Slack            |
| `SLACK_SIGNING_SECRET` | Signing secret for verifying requests |
| `SLACK_APP_TOKEN`      | App-level token for Socket Mode       |
| `SUPABASE_URL`         | Your Supabase project URL             |
| `SUPABASE_KEY`         | Supabase anon/public API key          |
| `PORT`                 | HTTP server port (default: 8080)      |

## Endpoints

- **`/`** - Main leaderboard page (HTML)
- **`/health`** - Health check endpoint (returns "Bot is running!")

## Database Schema

```sql
CREATE TABLE snipes (
  user_id TEXT PRIMARY KEY,
  count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Used by heartbeat.py
CREATE TABLE heartbeats (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your credentials
# Then run
python snipes_bot.py
```

### Migrating Existing Data

If you have an old `snipes_data.json` file:

```bash
python migrate_to_supabase.py
```

## Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed deployment instructions for Northflank and other platforms, including the heartbeat Cron Job (run with `python /app/heartbeat.py`).

## Project Structure

```
.
├── snipes_bot.py           # Main application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── .dockerignore          # Docker ignore rules
├── env.example            # Environment variables template
├── heartbeat.py           # Supabase keep-alive ping (Northflank Cron Job)
├── migrate_to_supabase.py # Migration script
├── README.md              # This file
├── QUICKSTART.md          # Quick setup guide
└── DEPLOYMENT.md          # Detailed deployment guide
```

## Contributing

This is a fun side project, but feel free to fork and customize for your team!

## License

MIT - Use it however you'd like!

## Support

Check the troubleshooting sections in:

- **[QUICKSTART.md](QUICKSTART.md)** - For setup issues
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - For deployment issues

---

Made with ❤️ for making Slack more fun!
