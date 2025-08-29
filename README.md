# 🎵 Spotify Queue Assistant

A web application that allows **anyone** to add songs to **your** Spotify queue through a simple web interface. Perfect for parties, gatherings, events, or sharing on social media!


## ✨ Key Features

- **Public Song Submission**: Anyone can add songs to your queue (no login required for visitors)
- **Owner Authentication**: You authenticate once, others simply use the app
- **Two Input Methods**: Submit by song name/artist or Spotify track link
- **Spotify Integration**: Uses official Spotify Web API
- **Real-time Queue Updates**: Songs appear directly in your Spotify queue
- **Simple Interface**: Clean, user-friendly web form

## 🚀 Quick Start

1. **Set up your Spotify App**:
   - Create a Spotify Developer app at [developer.spotify.com](https://developer.spotify.com)
   - Set redirect URI to: `http://127.0.0.1:8888/callback`

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Spotify credentials
   ```

3. **Install & Run**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   python main.py
   ```

4. **Authenticate Once**: Visit `http://127.0.0.1:8888/auth` and login with your Spotify account

5. **Share The Link**: Let others visit `http://127.0.0.1:8888` to add songs to your queue!

## 📁 Project Structure

- `main.py` - FastAPI web application
- `spotify_config.py` - Spotify API authentication and operations
- `templates/submit.html` - Web form interface
- `requirements.txt` - Python dependencies
- `.env.example` - Template for environment variables
- `SETUP.md` - Detailed setup instructions

## �️ Technical Details

### Requirements

- Python 3.9+
- Spotify Premium Account (for queue manipulation)
- Spotify Developer App credentials

### Dependencies

- **FastAPI**: Modern web framework
- **Spotipy**: Python client for Spotify Web API
- **Uvicorn**: ASGI web server
- **Jinja2**: HTML templating
- **Python-dotenv**: Environment variable management

### Authentication Flow

This app uses a unique authentication approach:
1. Only the queue owner (you) needs to authenticate with Spotify
2. Authentication is done once via OAuth
3. Your access token is securely stored in `.spotify_cache`
4. Visitors can use the app without any authentication

## 💡 Use Cases

- **Parties & Events**: Let guests add songs without passing your phone around
- **Social Media**: Share your queue link on your profiles
- **Remote Collaboration**: Let friends contribute to your playlist from anywhere
- **Office Music**: Team members can queue songs without interrupting workflow

## 🔒 Security Notes

- Your Spotify credentials are stored locally in `.env` (never committed to Git)
- OAuth tokens are cached in `.spotify_cache` (also excluded from Git)
- Anyone with the URL can add songs to your queue while the server is running
- The app requires a Spotify Premium account to control playback

## 🚀 Deployment Options

### Local Network Sharing
To make this available on your local network:
```bash
python main.py --host 0.0.0.0
```
Then others can connect via your local IP address: `http://your-ip-address:8888`

### Internet Deployment
For broader accessibility, consider deploying to:
- **Heroku**: Easy deployment with Procfile
- **Railway**: Simple Python app deployment
- **Digital Ocean App Platform**: Managed hosting
- **Render**: Free tier available for hobby projects

## 🔮 Future Enhancements

- **AI-Powered Song Recommendations**: Smart suggestions based on mood
- **Natural Language Processing**: "Play something upbeat" → finds matching songs
- **User-Specific Limits**: Prevent single user from dominating the queue
- **Mobile App**: Native mobile interface for song submission
- **Custom Branding**: Personalized themes for your events

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for their excellent documentation
- [Spotipy](https://github.com/plamere/spotipy) Python library
- [FastAPI](https://fastapi.tiangolo.com/) for the lightweight web framework

2. **Get your Spotify API credentials:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
   - Create a new app or use an existing one
   - Note down your Client ID and Client Secret
   - Add `http://localhost:8888/callback` to your app's Redirect URIs

3. **Fill in your `.env` file:**
   ```
   SPOTIFY_CLIENT_ID=your_actual_client_id_here
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   ```

### 3. Running the Application

**Make sure your virtual environment is activated:**
```bash
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows
```

**Run the application:**

```bash
python main.py
```

Or run the configuration test:
```bash
python spotify_config.py
```

## File Structure

- `spotify_config.py` - Configuration class for handling Spotify API credentials
- `main.py` - Example application entry point
- `.env.example` - Template for environment variables (safe to commit)
- `.env` - Your actual environment variables (DO NOT COMMIT)
- `.gitignore` - Ensures `.env` is not committed to Git

## Security Notes

- ✅ `.env.example` is safe to commit to Git
- ❌ Never commit your actual `.env` file with real credentials
- ✅ The `.gitignore` file prevents accidental commits of sensitive data
- ✅ Environment variables are validated at runtime

## Usage in Your Code

```python
from spotify_config import SpotifyConfig

# Load configuration
config = SpotifyConfig()
credentials = config.get_auth_credentials()

# Use credentials with your Spotify API client
client_id = credentials['client_id']
client_secret = credentials['client_secret']
redirect_uri = credentials['redirect_uri']
```
