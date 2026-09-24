# Deploying Snipes Bot to Northflank with Supabase

This guide will help you deploy your Slack bot to Northflank using Supabase as the database backend.

## Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Northflank Account**: Sign up at [northflank.com](https://northflank.com)
3. **Slack App**: Your Slack app should be configured with:
   - Bot Token (`SLACK_BOT_TOKEN`)
   - Signing Secret (`SLACK_SIGNING_SECRET`)
   - App Token (`SLACK_APP_TOKEN`) with Socket Mode enabled
   - **Required Bot Token Scopes**:
     - `app_mentions:read`
     - `channels:history`
     - `chat:write`
     - `files:read` (required to detect image attachments)
     - `users:read`

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
- Ensure your bot has the `files:read` scope (required to detect images)
- Check Northflank logs for errors
- Remember: snipes only count when a message has BOTH a user tag AND an image!

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

## Keeping Supabase Alive (Heartbeat)

If you're using a free Supabase project, it may be paused after a period of inactivity. To prevent this, a heartbeat script (`heartbeat.py`) inserts a row into a `heartbeats` table on a schedule. It runs as a separate Northflank Cron Job built from the same `Dockerfile`, which copies all application code (including `heartbeat.py`) into `/app`.

### 1. Create the `heartbeats` table

In the Supabase SQL Editor, run:

```sql
CREATE TABLE IF NOT EXISTS heartbeats (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

If Row Level Security is enabled on this table, add a policy that allows inserts with your anon key, or the heartbeat will fail.

### 2. Create the Cron Job on Northflank

1. In your Northflank project dashboard, click **Create** and select **Cron Job**.
2. **Source**: Connect the same GitHub repository and branch (`master`) used by your main service.
3. **Build settings**: Build type Dockerfile, Dockerfile path `/Dockerfile`, build context `/`.
4. **Cron schedule**: Set it to run periodically, for example every 4 days: `0 0 */4 * *`.
5. **CMD override**: Enter the absolute path: `python /app/heartbeat.py`
   - Do not use `python heartbeat.py`. Northflank may start the container in `/workspace` instead of `/app`, which fails with `can't open file '/workspace/heartbeat.py'`.
6. **Environment**: Add `SUPABASE_URL` and `SUPABASE_KEY` (same values as the main service).
7. Click **Create Cron Job**.

### 3. Build, deploy, and verify

1. Under **Builds**, wait for the build of your latest commit to succeed.
2. Click **Deploy** on that build. The job keeps running the previously deployed image until you do this.
3. Under **Runs**, trigger a manual run and open its logs. You should see `Heartbeat sent successfully.`
4. Confirm a new row appeared in the `heartbeats` table in Supabase.

### Heartbeat troubleshooting

- **`can't open file '.../heartbeat.py'`**: Set the CMD override to `python /app/heartbeat.py`. If it persists, check that the deployed build is from a commit where the `Dockerfile` uses `COPY . .`.
- **Build fails with `failed to resolve source metadata for docker.io/library/python:3.11-slim`**: Northflank's image mirror or Docker Hub had a temporary problem. Click **Rebuild**. If it keeps failing, change the first line of the `Dockerfile` to `FROM public.ecr.aws/docker/library/python:3.11-slim`.
- **Run shows success but no row appears**: The script logs errors but still exits with code 0. Read the run logs for `Error sending heartbeat` or a missing `SUPABASE_URL`/`SUPABASE_KEY` message.
- **New commits don't reach the job**: Enable automatic builds for `master` under **Build options**, and remember to deploy each new build.

## Weekly Leaderboard Summary

`weekly_summary.py` posts the top 10 all-time leaderboard to a Slack channel. Run it as a Northflank Cron Job the same way as the heartbeat:

1. **Cron schedule**: e.g. Mondays at 9am UTC: `0 9 * * 1`.
2. **CMD override**: `python /app/weekly_summary.py`
3. **Environment**: `SLACK_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`, and `SLACK_CHANNEL_ID` (right-click the channel → View channel details → copy the ID at the bottom).
4. Invite the bot to that channel (`/invite @your-bot`), or the post fails with `not_in_channel`.

Unlike the heartbeat, this script exits non-zero on failure, so failed runs show as failed in Northflank.
