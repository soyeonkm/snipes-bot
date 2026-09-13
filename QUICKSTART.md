# Quick Start Guide

## What Changed?

Your Slack bot has been updated to use **Supabase** for persistent storage instead of local JSON files, and is now ready to deploy on **Northflank**.

## Files Created/Modified

### Modified:

- `snipes_bot.py` - Now uses Supabase instead of JSON file storage
- `requirements.txt` - Added `supabase` dependency

### Created:

- `Dockerfile` - For containerized deployment on Northflank
- `.dockerignore` - Excludes unnecessary files from Docker image
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `env.example` - Template for environment variables
- `migrate_to_supabase.py` - Script to migrate existing snipe data

## Quick Setup Steps

### 1. Set Up Supabase (5 minutes)

1. Go to [supabase.com](https://supabase.com) and create a project
2. In SQL Editor, run:
   ```sql
   CREATE TABLE snipes (
     user_id TEXT PRIMARY KEY,
     count INTEGER NOT NULL DEFAULT 0,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```
3. Copy your `URL` and `anon` key from Project Settings → API

### 2. Create Your .env File

Copy `env.example` to `.env` and fill in your values:

```bash
cp env.example .env
```

Then edit `.env` with your actual credentials:

- Slack tokens (you already have these)
- Supabase URL and key (from step 1)

### 3. (Optional) Migrate Existing Data

If you have `snipes_data.json` with existing snipe counts:

```bash
python migrate_to_supabase.py
```

### 4. Test Locally

```bash
pip install -r requirements.txt
python snipes_bot.py
```

Test in Slack by tagging someone. The snipe count should now be stored in Supabase!

### 5. Deploy to Northflank

1. Push your code to GitHub
2. Create a new service on [Northflank](https://northflank.com)
3. Connect your GitHub repo
4. Add environment variables (same as your .env file)
5. Deploy!

See `DEPLOYMENT.md` for detailed deployment instructions.

### 6. (Optional) Keep Supabase Awake

Free Supabase projects pause when idle. Create a `heartbeats` table and a Northflank Cron Job that runs `python /app/heartbeat.py` on a schedule. Full steps are in the "Keeping Supabase Alive (Heartbeat)" section of `DEPLOYMENT.md`.

## Environment Variables You Need

| Variable               | Where to Get It                                  |
| ---------------------- | ------------------------------------------------ |
| `SLACK_BOT_TOKEN`      | Slack App → OAuth & Permissions                  |
| `SLACK_SIGNING_SECRET` | Slack App → Basic Information                    |
| `SLACK_APP_TOKEN`      | Slack App → Basic Information → App-Level Tokens |
| `SUPABASE_URL`         | Supabase → Settings → API                        |
| `SUPABASE_KEY`         | Supabase → Settings → API (use anon/public key)  |

## Leaderboard Website

Your bot now includes a **live leaderboard website**!

When deployed, you can access:

- **`/`** - Beautiful leaderboard showing top snipers with their counts
- **`/health`** - Health check endpoint for monitoring

The leaderboard features:

- 🥇 🥈 🥉 Medals for top 3 positions
- Real Slack user names (fetched from Slack API)
- Responsive design that works on mobile
- Auto-refreshes data from Supabase
- Shows top 50 users

**How to Snipe**: Tag someone in Slack AND attach a photo to the message! 📸

## Benefits of This Setup

✅ **Persistent Storage** - Data survives restarts and redeploys
✅ **Scalable** - Supabase handles database scaling automatically
✅ **Free Tier** - Both Supabase and Northflank offer generous free tiers
✅ **No File System** - Works perfectly with containerized deployments
✅ **Easy Monitoring** - View data directly in Supabase dashboard
✅ **Public Leaderboard** - Share the URL with your team to see rankings!

## Need Help?

- **Deployment Issues**: Check `DEPLOYMENT.md` for detailed troubleshooting
- **Database Issues**: Verify your Supabase credentials and table exists
- **Bot Issues**: Check Northflank logs for error messages
