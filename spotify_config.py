"""
Spotify API Configuration and Environment Variable Handler

This module loads environment variables for Spotify API authentication
and provides a secure way to access them in your application.
"""

import os
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from queue_ai import QueueAI

# Load environment variables from .env file
load_dotenv()

class SpotifyConfig:
    """
    Configuration class for Spotify API credentials and operations.
    """
    
    def __init__(self):
        """
        Initialize Spotify configuration by loading environment variables.
        Raises ValueError if required environment variables are missing.
        """
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.redirect_uri = os.getenv('SPOTIFY_REDIRECT_URI')
        
        # Validate that all required environment variables are present
        self._validate_config()
        
        # Initialize Spotify client with required scopes for queue operations
        self.scope = "user-modify-playback-state,user-read-playback-state"
        self.sp = None
        self.search_sp = None  # Separate client for search operations
        
        # Initialize the owner's authenticated client (you authenticate once)
        self._init_owner_client()
        
        # Initialize AI queue management
        self.queue_ai = None
        
    def _validate_config(self):
        """
        Validate that all required environment variables are set.
        Raises ValueError if any required variable is missing.
        """
        missing_vars = []
        
        if not self.client_id:
            missing_vars.append('SPOTIFY_CLIENT_ID')
        
        if not self.client_secret:
            missing_vars.append('SPOTIFY_CLIENT_SECRET')
        
        if not self.redirect_uri:
            missing_vars.append('SPOTIFY_REDIRECT_URI')
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file and ensure all variables are set."
            )
    
    def _init_owner_client(self):
        """
        Initialize the owner's Spotify client (the person whose queue will be controlled).
        This should be called once to authenticate the queue owner.
        """
        try:
            auth_manager = SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
                cache_path=".spotify_cache",
                show_dialog=False,
                open_browser=False
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            # Initialize search client (doesn't require user auth)
            search_auth = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.search_sp = spotipy.Spotify(auth_manager=search_auth)
            
        except Exception as e:
            print(f"Warning: Could not initialize owner client: {e}")
            # Still initialize search client for public operations
            search_auth = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.search_sp = spotipy.Spotify(auth_manager=search_auth)
    
    def get_auth_credentials(self):
        """
        Returns a dictionary with authentication credentials.
        
        Returns:
            dict: Dictionary containing client_id, client_secret, and redirect_uri
        """
        return {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri
        }
    
    def get_owner_client(self):
        """
        Get the authenticated Spotify client for the queue owner.
        This is used for operations that require user permissions (like adding to queue).
        
        Returns:
            spotipy.Spotify: Authenticated Spotify client for queue operations
        """
        if not self.sp:
            raise Exception("Owner not authenticated. Please authenticate first via /auth endpoint.")
        
        # Initialize AI queue management if not already done
        if not self.queue_ai and self.sp:
            try:
                self.queue_ai = QueueAI(self.sp)
            except Exception as e:
                print(f"Warning: Could not initialize Queue AI: {e}")
        
        return self.sp
    
    def get_search_client(self):
        """
        Get a Spotify client for search operations (doesn't require user auth).
        This can be used by anyone to search for tracks.
        
        Returns:
            spotipy.Spotify: Spotify client with Client Credentials auth
        """
        if not self.search_sp:
            auth_manager = SpotifyClientCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            self.search_sp = spotipy.Spotify(auth_manager=auth_manager)
        return self.search_sp
    
    def is_owner_authenticated(self):
        """
        Check if the queue owner is authenticated.
        
        Returns:
            bool: True if owner is authenticated, False otherwise
        """
        try:
            if self.sp:
                # Test the connection
                self.sp.current_user()
                return True
        except:
            pass
        return False
    
    def is_spotify_link(self, query: str) -> bool:
        """
        Check if the query is a Spotify link or URI.
        
        Args:
            query (str): The input query
            
        Returns:
            bool: True if it's a Spotify link/URI, False otherwise
        """
        spotify_patterns = [
            r'https?://open\.spotify\.com/track/([a-zA-Z0-9]+)',
            r'spotify:track:([a-zA-Z0-9]+)'
        ]
        
        for pattern in spotify_patterns:
            if re.search(pattern, query):
                return True
        return False
    
    def extract_track_id(self, query: str) -> str | None:
        """
        Extract track ID from Spotify link or URI.
        
        Args:
            query (str): Spotify link or URI
            
        Returns:
            str | None: Track ID if found, None otherwise
        """
        patterns = [
            r'https?://open\.spotify\.com/track/([a-zA-Z0-9]+)',
            r'spotify:track:([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        return None
    
    def search_track(self, query: str, limit: int = 1):
        """
        Search for a track by name/artist using Client Credentials (no user auth needed).
        
        Args:
            query (str): Search query (song name, artist, etc.)
            limit (int): Number of results to return
            
        Returns:
            dict: Search results from Spotify API
        """
        try:
            sp = self.get_search_client()
            results = sp.search(q=query, type='track', limit=limit)
            return results
        except Exception as e:
            raise Exception(f"Error searching for track: {str(e)}")
    
    def get_track_info(self, track_id: str):
        """
        Get track information by track ID using search client.
        
        Args:
            track_id (str): Spotify track ID
            
        Returns:
            dict: Track information from Spotify API
        """
        try:
            sp = self.get_search_client()
            track = sp.track(track_id)
            return track
        except Exception as e:
            raise Exception(f"Error getting track info: {str(e)}")
    
    def add_to_queue(self, track_uri: str):
        """
        Add a track to the owner's queue.
        
        Args:
            track_uri (str): Spotify track URI (spotify:track:...)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            sp = self.get_owner_client()
            sp.add_to_queue(track_uri)
            return True
        except Exception as e:
            raise Exception(f"Error adding track to queue: {str(e)}")
    
    def process_query(self, query: str):
        """
        Process a user query with AI enhancements - either search for a song or add Spotify link to queue.
        
        Args:
            query (str): User input (song name or Spotify link)
            
        Returns:
            dict: Result with success status, message, track info, and AI recommendations
        """
        query = query.strip()
        
        try:
            if self.is_spotify_link(query):
                # Handle Spotify link
                track_id = self.extract_track_id(query)
                if not track_id:
                    return {
                        'success': False,
                        'message': 'Invalid Spotify link format',
                        'track': None,
                        'recommendations': []
                    }
                
                # Get track info
                track = self.get_track_info(track_id)
                if not track:
                    return {
                        'success': False,
                        'message': 'Could not find track information',
                        'track': None,
                        'recommendations': []
                    }
                
            else:
                # Handle song search
                results = self.search_track(query)
                
                if not results or not results.get('tracks', {}).get('items'):
                    return {
                        'success': False,
                        'message': f"❌ No tracks found for '{query}'. Try a different search term.",
                        'track': None,
                        'recommendations': []
                    }
                
                # Get the first (best) result
                track = results['tracks']['items'][0]
            
            # Use AI to check if we should add this track
            if self.queue_ai:
                ai_result = self.queue_ai.process_submission(track)
                
                if not ai_result['allowed']:
                    return {
                        'success': False,
                        'message': f"🤔 {ai_result['reason']}",
                        'track': track,
                        'recommendations': ai_result['recommendations'],
                        'suggestion': ai_result.get('suggestion', '')
                    }
            
            # Add to queue
            track_uri = track['uri']
            self.add_to_queue(track_uri)
            
            # Get AI recommendations for the successfully added track
            recommendations = []
            if self.queue_ai:
                ai_result = self.queue_ai.process_submission(track)
                recommendations = ai_result.get('recommendations', [])
            
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            success_message = f"✅ Added '{track['name']}' by {artist_names} to your queue!"
            
            if recommendations:
                rec_names = []
                for rec in recommendations[:2]:
                    rec_artists = ', '.join(rec['artists'])
                    rec_names.append(f"{rec['name']} by {rec_artists}")
                success_message += f"\n🎵 Others might also enjoy: {', '.join(rec_names)}"
            
            return {
                'success': True,
                'message': success_message,
                'track': track,
                'recommendations': recommendations
            }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ Error: {str(e)}",
                'track': None,
                'recommendations': []
            }

def main():
    """
    Example usage of the SpotifyConfig class.
    """
    try:
        # Initialize Spotify configuration
        config = SpotifyConfig()
        
        # Get credentials
        credentials = config.get_auth_credentials()
        
        print("✅ Environment variables loaded successfully!")
        print(f"Client ID: {credentials['client_id'][:8]}..." if credentials['client_id'] else "Not set")
        print(f"Redirect URI: {credentials['redirect_uri']}")
        
        # Example: Using the credentials (replace with your actual Spotify API setup)
        print("\n🎵 Ready to connect to Spotify API!")
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\n📝 To fix this:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your actual Spotify API credentials")
        print("3. Get credentials from: https://developer.spotify.com/dashboard/applications")

if __name__ == "__main__":
    main()
