"""
AI-Powered Queue Management System

This module provides intelligent queue management features including:
- Smart duplicate prevention
- Song recommendations based on current queue
- Queue flow analysis and suggestions
- Usage analytics and popular track tracking
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
import spotipy

class QueueAI:
    """
    AI-powered queue management system.
    """
    
    def __init__(self, spotify_client):
        """
        Initialize the QueueAI system.
        
        Args:
            spotify_client: Authenticated Spotify client
        """
        self.sp = spotify_client
        self.analytics_file = "queue_analytics.json"
        self.recent_tracks = []  # Track recent additions
        self.load_analytics()
    
    def load_analytics(self):
        """Load analytics data from file."""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r') as f:
                    self.analytics = json.load(f)
            else:
                self.analytics = {
                    'total_submissions': 0,
                    'popular_tracks': {},
                    'popular_artists': {},
                    'recent_activity': [],
                    'duplicate_prevention': 0,
                    'recommendations_given': 0
                }
        except Exception:
            self.analytics = {
                'total_submissions': 0,
                'popular_tracks': {},
                'popular_artists': {},
                'recent_activity': [],
                'duplicate_prevention': 0,
                'recommendations_given': 0
            }
    
    def save_analytics(self):
        """Save analytics data to file."""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2)
        except Exception:
            pass  # Fail silently if can't save
    
    def is_duplicate_or_similar(self, track_info: dict) -> Tuple[bool, str]:
        """
        Check if a track is a duplicate or too similar to recent additions.
        
        Args:
            track_info: Spotify track information
            
        Returns:
            Tuple of (is_duplicate, reason)
        """
        track_id = track_info['id']
        track_name = track_info['name'].lower()
        artist_names = [artist['name'].lower() for artist in track_info['artists']]
        
        # Check recent tracks (last 10 additions)
        for recent in self.recent_tracks[-10:]:
            # Exact same track
            if recent['id'] == track_id:
                return True, f"This exact song was already added recently"
            
            # Same song name by same artist
            if (recent['name'].lower() == track_name and 
                any(artist.lower() in artist_names for artist in recent['artists'])):
                return True, f"Very similar song by the same artist was recently added"
        
        return False, ""
    
    def add_track_to_recent(self, track_info: dict):
        """
        Add a track to the recent tracks list and update analytics.
        
        Args:
            track_info: Spotify track information
        """
        track_data = {
            'id': track_info['id'],
            'name': track_info['name'],
            'artists': [artist['name'] for artist in track_info['artists']],
            'added_at': datetime.now().isoformat(),
            'popularity': track_info.get('popularity', 0)
        }
        
        self.recent_tracks.append(track_data)
        
        # Keep only last 20 tracks in memory
        if len(self.recent_tracks) > 20:
            self.recent_tracks = self.recent_tracks[-20:]
        
        # Update analytics
        track_key = f"{track_info['name']} - {track_info['artists'][0]['name']}"
        self.analytics['popular_tracks'][track_key] = self.analytics['popular_tracks'].get(track_key, 0) + 1
        
        for artist in track_info['artists']:
            self.analytics['popular_artists'][artist['name']] = self.analytics['popular_artists'].get(artist['name'], 0) + 1
        
        self.analytics['total_submissions'] += 1
        self.analytics['recent_activity'].append({
            'track': track_key,
            'timestamp': datetime.now().isoformat(),
            'popularity': track_info.get('popularity', 0)
        })
        
        # Keep only last 100 activities
        if len(self.analytics['recent_activity']) > 100:
            self.analytics['recent_activity'] = self.analytics['recent_activity'][-100:]
        
        self.save_analytics()
    
    def get_recommendations(self, track_info: dict, limit: int = 3) -> List[Dict]:
        """
        Get AI-powered recommendations based on the added track and current queue context.
        
        Args:
            track_info: The track that was just added
            limit: Number of recommendations to return
            
        Returns:
            List of recommended track information
        """
        try:
            # Get Spotify's recommendations based on the track
            recommendations = self.sp.recommendations(
                seed_tracks=[track_info['id']], 
                limit=limit * 2  # Get more to filter out duplicates
            )
            
            filtered_recommendations = []
            for rec in recommendations['tracks']:
                # Don't recommend something that's already in recent tracks or is the same artist
                is_dup, _ = self.is_duplicate_or_similar(rec)
                if not is_dup:
                    filtered_recommendations.append({
                        'name': rec['name'],
                        'artists': [artist['name'] for artist in rec['artists']],
                        'spotify_url': rec['external_urls']['spotify'],
                        'popularity': rec.get('popularity', 0),
                        'preview_url': rec.get('preview_url')
                    })
                
                if len(filtered_recommendations) >= limit:
                    break
            
            self.analytics['recommendations_given'] += len(filtered_recommendations)
            self.save_analytics()
            
            return filtered_recommendations
            
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []
    
    def get_queue_insights(self) -> Dict:
        """
        Get insights about the current queue and usage patterns.
        
        Returns:
            Dictionary with queue insights
        """
        insights = {
            'total_submissions': self.analytics['total_submissions'],
            'duplicate_prevention_count': self.analytics['duplicate_prevention'],
            'recommendations_given': self.analytics['recommendations_given'],
            'top_artists': [],
            'top_tracks': [],
            'recent_activity_count': len(self.analytics['recent_activity'])
        }
        
        # Get top artists
        if self.analytics['popular_artists']:
            top_artists = sorted(
                self.analytics['popular_artists'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            insights['top_artists'] = [{'name': name, 'count': count} for name, count in top_artists]
        
        # Get top tracks
        if self.analytics['popular_tracks']:
            top_tracks = sorted(
                self.analytics['popular_tracks'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            insights['top_tracks'] = [{'name': name, 'count': count} for name, count in top_tracks]
        
        return insights
    
    def process_submission(self, track_info: dict) -> Dict:
        """
        Process a track submission with AI enhancements.
        
        Args:
            track_info: Spotify track information
            
        Returns:
            Dictionary with processing results including recommendations
        """
        # Check for duplicates/similar tracks
        is_duplicate, duplicate_reason = self.is_duplicate_or_similar(track_info)
        
        if is_duplicate:
            self.analytics['duplicate_prevention'] += 1
            self.save_analytics()
            
            return {
                'allowed': False,
                'reason': duplicate_reason,
                'recommendations': self.get_recommendations(track_info, limit=2),
                'suggestion': "Try one of these similar tracks instead!"
            }
        
        # Track is allowed, add to recent and get recommendations
        self.add_track_to_recent(track_info)
        recommendations = self.get_recommendations(track_info)
        
        return {
            'allowed': True,
            'reason': "Track added successfully!",
            'recommendations': recommendations,
            'suggestion': "Others might also enjoy these similar tracks:" if recommendations else None
        }