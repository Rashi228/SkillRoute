import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
from config import settings

class YouTubeClient:
    def __init__(self):
        self.api_key = settings.YOUTUBE_API_KEY
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is not set")
            
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.max_results = int(os.environ.get("YOUTUBE_SEARCH_MAX_RESULTS", "5"))
        self.calls_made = 0
        
    def search_videos(self, query: str) -> List[Dict[str, Any]]:
        """
        Executes a search against the YouTube Data API for the given query.
        Returns a list of raw video metadata dictionaries.
        """
        try:
            self.calls_made += 1
            request = self.youtube.search().list(
                q=query,
                part="snippet",
                type="video",
                maxResults=self.max_results
            )
            response = request.execute()
            
            videos = []
            for item in response.get("items", []):
                # Ensure we have video IDs
                if item.get("id", {}).get("kind") == "youtube#video":
                    videos.append(item)
                    
            # We want to fetch duration, views, likes which requires videos().list()
            return self._enrich_video_metadata(videos)
            
        except HttpError as e:
            print(f"YouTube API Error: {e}")
            raise RuntimeError(f"YouTube API Error: {e}")
        except Exception as e:
            print(f"Unexpected error in YouTube Client: {e}")
            raise RuntimeError(f"Unexpected error in YouTube Client: {e}")
    def _enrich_video_metadata(self, search_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fetches statistics and content details for discovered videos.
        """
        if not search_items:
            return []
            
        video_ids = [item["id"]["videoId"] for item in search_items]
        
        try:
            self.calls_made += 1
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids)
            )
            response = request.execute()
            
            return response.get("items", [])
        except HttpError as e:
            print(f"YouTube API Enrichment Error: {e}")
            raise RuntimeError(f"YouTube API Enrichment Error: {e}")
