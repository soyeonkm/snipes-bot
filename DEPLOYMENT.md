# Deploying Snipes Bot to Northflank with Supabase

This guide will help you deploy your Slack bot to Northflank using Supabase as the database backend.

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Northflank Account**: Sign up at [northflank.com](https://northflank.com)
3. **Slack App**: Your Slack app should be configured with:
   - Bot Token (`SLACK_BOT_TOKEN`)
   - Signing Secret (`SLACK_SIGNING_SECRET`)
   - App Token (`SLACK_APP_TOKEN`) with Socket Mode enabled

## Step 1: Set up Supabase Database

1. **Create a new Supabase project**:

   - Go to [app.supabase.com](https://app.supabase.com)
   - Click "New Project"
   - Choose a name and password
   - Select a region close to your users

2. **Create the `snipes` table**:

   - Go to the SQL Editor in your Supabase dashboard
   - Run this SQL command:

   ```sql
   CREATE TABLE snipes (
     user_id TEXT PRIMARY KEY,
     count INTEGER NOT NULL DEFAULT 0,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Optional: Add an updated_at trigger
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
     NEW.updated_at = NOW();
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   CREATE TRIGGER update_snipes_updated_at
     BEFORE UPDATE ON snipes
     FOR EACH ROW
     EXECUTE FUNCTION update_updated_at_column();
   ```

3. **Get your Supabase credentials**:
   - Go to Project Settings → API
   - Copy the `URL` (this is your `SUPABASE_URL`)
   - Copy the `anon public` key (this is your `SUPABASE_KEY`)

## Step 2: Deploy to Northflank

### Option A: Deploy from GitHub (Recommended)

1. **Push your code to GitHub**:

   ```bash
   git add .
   git commit -m "Add Supabase integration and Northflank deployment"
   git push origin master
   ```

2. **Create a new service on Northflank**:

   - Log in to [app.northflank.com](https://app.northflank.com)
   - Click "Create Service"
   - Select "Combined Service" (for building and running)
   - Connect your GitHub repository

3. **Configure build settings**:

   - Build Type: Dockerfile
   - Dockerfile Path: `Dockerfile`
   - Context: `/`

4. **Configure runtime settings**:
   - Port: `8080`
   - Health check: HTTP GET `/health` (returns "Bot is running!")

### Option B: Deploy with Docker

1. **Build and push your Docker image**:

   ```bash
   docker build -t your-registry/snipes-bot:latest .
   docker push your-registry/snipes-bot:latest
   ```

2. **Create service on Northflank**:
   - Select "Deployment Service"
   - Use your Docker image

## Step 3: Configure Environment Variables

In your Northflank service settings, add these environment variables:

| Variable               | Value                     | Where to Get It                                           |
| ---------------------- | ------------------------- | --------------------------------------------------------- |
| `SLACK_BOT_TOKEN`      | `xoxb-...`                | Slack App Settings → OAuth & Permissions                  |
| `SLACK_SIGNING_SECRET` | Your signing secret       | Slack App Settings → Basic Information                    |
| `SLACK_APP_TOKEN`      | `xapp-...`                | Slack App Settings → Basic Information → App-Level Tokens |
| `SUPABASE_URL`         | `https://xxx.supabase.co` | Supabase Project → Settings → API                         |
| `SUPABASE_KEY`         | Your anon key             | Supabase Project → Settings → API                         |
| `PORT`                 | `8080`                    | Usually set automatically by Northflank                   |

## Step 4: Deploy and Verify

1. **Deploy your service**:

   - Click "Deploy" in Northflank
   - Wait for the build and deployment to complete

2. **Check logs**:

   - Monitor the logs in Northflank dashboard
   - Look for successful Slack connection messages

3. **Test your bot**:

   - Go to your Slack workspace
   - Tag someone in a message: `Hello @someone!`
   - The bot should respond with the snipe count

4. **View the leaderboard**:
   - Get your Northflank service URL from the dashboard
   - Visit the URL in your browser to see the live leaderboard
   - Share the URL with your team!

## Troubleshooting

### Bot not responding

- Check that Socket Mode is enabled in your Slack app settings
- Verify all environment variables are set correctly
- Check Northflank logs for errors

### Database connection errors

- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Check that the `snipes` table exists in Supabase
- Ensure your Supabase project is active (not paused)

### Deployment fails

- Check Dockerfile syntax
- Verify all dependencies are in `requirements.txt`
- Check build logs in Northflank

### Leaderboard not showing data

- Verify the Supabase connection is working (check logs)
- Ensure there's at least one snipe in the database
- Check that the Slack bot token has `users:read` permission
- Try accessing `/health` endpoint first to verify server is running

## Monitoring

- **Northflank**: Monitor service health, logs, and metrics in the dashboard
- **Supabase**: View data in the Table Editor, monitor API usage in Settings
- **Slack**: Use the Slack App management page to see event deliveries

## Optional: Auto-scaling

To handle varying loads:

1. In Northflank, go to your service settings
2. Configure scaling rules based on CPU/memory usage
3. Set minimum and maximum instance counts

## Cost Optimization

- **Supabase**: Free tier includes 500MB database and 2GB bandwidth
- **Northflank**: Free tier includes 2 services with limited resources
- Both platforms scale with usage, monitor your usage regularly

## Migrating Existing Data

If you have existing snipe counts in `snipes_data.json`:

```python
# migration_script.py
import json
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Load old data
with open('snipes_data.json', 'r') as f:
    old_data = json.load(f)

# Migrate to Supabase
for user_id, count in old_data.items():
    supabase.table("snipes").upsert({
        "user_id": user_id,
        "count": count
    }).execute()
    print(f"Migrated {user_id}: {count} snipes")

print("Migration complete!")
```

Run this script locally before deploying to Northflank.
