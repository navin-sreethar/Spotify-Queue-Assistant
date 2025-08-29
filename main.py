"""
Spotify AI Queue Assistant - FastAPI Web Application

A web application that allows users to add songs to their Spotify queue
by submitting song names or Spotify track links through an HTML form.
"""

from fastapi import FastAPI, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
import uvicorn
from spotify_config import SpotifyConfig
from typing import Optional

# Initialize FastAPI app
app = FastAPI(title="Spotify AI Queue Assistant")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize Spotify configuration
spotify_config = SpotifyConfig()

@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    """
    Display the song submission form for anyone to use.
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        TemplateResponse: HTML form page
    """
    # Check if the queue owner (you) is authenticated
    if not spotify_config.is_owner_authenticated():
        return templates.TemplateResponse(
            "submit.html",
            {
                "request": request,
                "message": "⚠️  Queue owner needs to authenticate first. Owner should visit /auth to set up the queue.",
                "message_type": "info"
            }
        )
    
    return templates.TemplateResponse(
        "submit.html", 
        {"request": request}
    )

@app.get("/auth")
async def spotify_auth():
    """
    Initiate Spotify OAuth flow for the queue owner (you).
    
    Returns:
        RedirectResponse: Redirect to Spotify authorization URL
    """
    try:
        sp = spotify_config.get_owner_client()
        auth_url = sp.auth_manager.get_authorize_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        # If not authenticated, create the auth URL manually
        from spotipy.oauth2 import SpotifyOAuth
        auth_manager = SpotifyOAuth(
            client_id=spotify_config.client_id,
            client_secret=spotify_config.client_secret,
            redirect_uri=spotify_config.redirect_uri,
            scope=spotify_config.scope,
            cache_path=".spotify_cache",
            show_dialog=False,
            open_browser=False
        )
        auth_url = auth_manager.get_authorize_url()
        return RedirectResponse(url=auth_url)

@app.get("/callback")
async def spotify_callback(request: Request, code: Optional[str] = Query(None), error: Optional[str] = Query(None)):
    """
    Handle Spotify OAuth callback for the queue owner.
    
    Args:
        request (Request): FastAPI request object
        code (str): Authorization code from Spotify
        error (str): Error from Spotify (if any)
        
    Returns:
        RedirectResponse: Redirect back to main page
    """
    if error:
        return templates.TemplateResponse(
            "submit.html",
            {
                "request": request,
                "message": f"❌ Authentication failed: {error}",
                "message_type": "error"
            }
        )
    
    if code:
        try:
            # Reinitialize the owner client with the authorization code
            from spotipy.oauth2 import SpotifyOAuth
            import spotipy
            
            auth_manager = SpotifyOAuth(
                client_id=spotify_config.client_id,
                client_secret=spotify_config.client_secret,
                redirect_uri=spotify_config.redirect_uri,
                scope=spotify_config.scope,
                cache_path=".spotify_cache",
                show_dialog=False,
                open_browser=False
            )
            
            # Get the token using the authorization code
            auth_manager.get_access_token(code)
            spotify_config.sp = spotipy.Spotify(auth_manager=auth_manager)
            
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "message": "✅ Successfully authenticated! Your queue is now ready for submissions from others.",
                    "message_type": "success"
                }
            )
        except Exception as e:
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "message": f"❌ Authentication error: {str(e)}",
                    "message_type": "error"
                }
            )
    
    return RedirectResponse(url="/")

@app.post("/", response_class=HTMLResponse)
async def submit_song(request: Request, query: str = Form(...)):
    """
    Handle song submission from the form.
    Anyone can use this to add songs to the owner's queue.
    
    Args:
        request (Request): FastAPI request object
        query (str): Song name or Spotify link from form
        
    Returns:
        TemplateResponse: HTML response with success/error message
    """
    try:
        # Check if the queue owner is authenticated
        if not spotify_config.is_owner_authenticated():
            return templates.TemplateResponse(
                "submit.html",
                {
                    "request": request,
                    "message": "⚠️  Queue owner needs to authenticate first. Please ask the owner to visit /auth.",
                    "message_type": "error",
                    "query": query
                }
            )
        
        # Process the query using SpotifyConfig (will add to owner's queue)
        result = spotify_config.process_query(query)
        
        if result['success']:
            message = result['message']
            message_type = "success"
        else:
            message = result['message']
            message_type = "error"
            
    except Exception as e:
        error_msg = str(e)
        if "No active device" in error_msg:
            message = "❌ No active Spotify device found. Please ask the owner to open Spotify on any device and start playing music, then try again."
            message_type = "error"
        else:
            message = f"❌ Error: {error_msg}"
            message_type = "error"
    
    return templates.TemplateResponse(
        "submit.html",
        {
            "request": request,
            "message": message,
            "message_type": message_type,
            "query": query
        }
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "app": "Spotify AI Queue Assistant",
        "version": "1.0.0"
    }

def main():
    """
    Run the FastAPI application.
    """
    print("🎵 Starting Spotify AI Queue Assistant...")
    print("📱 Open your browser and go to: http://127.0.0.1:8888")
    print("🎶 Add songs to your Spotify queue!")
    print("\n" + "="*50)
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8888,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
