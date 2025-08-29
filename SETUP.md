# 🎵 Spotify Queue Assistant - Setup Guide

## What This Does

This creates a **public web link** that allows **other people** to add songs to **YOUR** Spotify queue. Perfect for parties, gatherings, or sharing on your social media profiles!

## How It Works

1. **You** (the queue owner) authenticate once with Spotify
2. **Anyone** can visit your web link and submit songs
3. **All songs** get added to **your** Spotify queue automatically
4. **No authentication required** for visitors

## Setup Steps

### Step 1: Configure Spotify App Settings

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
2. Open your app settings
3. Click "Edit Settings" 
4. In "Redirect URIs", add: `http://127.0.0.1:8888/callback`
5. Click "Save"

**Note**: Spotify requires the explicit loopback IP `127.0.0.1` (not `localhost`) for HTTP redirect URIs.

### Step 2: Start the Server

```bash
cd "/Users/navin/Desktop/Projects/Spotify AI Queue Assistant"
source .venv/bin/activate
python main.py
```

The server will start at: `http://127.0.0.1:8888`

### Step 3: Authenticate Yourself (One Time)

1. Visit: `http://127.0.0.1:8888/auth`
2. Login with **your** Spotify account (the one with the queue you want to control)
3. Grant permissions
4. You'll be redirected back with a success message

### Step 4: Share the Public Link

Now anyone can visit: `http://127.0.0.1:8888`

They can:
- ✅ Submit song names ("Bohemian Rhapsody")
- ✅ Submit Spotify links (https://open.spotify.com/track/...)
- ✅ No login required for them
- ✅ Songs go directly to YOUR queue

## Important Notes

- ⚠️  Make sure Spotify is **open and playing** on one of your devices
- 🔐 Only **you** need to authenticate (once)
- 🌐 Others just visit the link and submit songs
- 📱 Works great for parties, social media, etc.

## Sharing Your Link

You can share `http://127.0.0.1:8888` with friends, or if you deploy this to a server, you'd share that URL instead.

## Troubleshooting

**"No active device found"**: Open Spotify on any device and start playing music.

**"Queue owner needs to authenticate"**: Visit `/auth` to re-authenticate.

**Redirect URI errors**: Make sure you're using `http://127.0.0.1:8888/callback` in your Spotify app settings (not localhost).
