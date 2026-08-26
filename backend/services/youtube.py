import requests
import isodate
from config import settings
from typing import List, Dict

def search_youtube(query: str, max_results: int = 2) -> List[Dict]:
    """
    Search YouTube Data API and return structured video metadata.
    Returns empty list if API key is missing or quota exceeded.
    """
    if not settings.YOUTUBE_API_KEY:
        return []
        
    try:
        # Step 1: Search for videos
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "videoDuration": "long", # Bias towards comprehensive content
            "key": settings.YOUTUBE_API_KEY
        }
        
        search_res = requests.get(search_url, params=search_params)
        if search_res.status_code != 200:
            print(f"YouTube Search API Error: {search_res.text}")
            return []
            
        search_data = search_res.json()
        video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
        
        if not video_ids:
            return []
            
        # Step 2: Get video details (Duration, Statistics)
        video_url = "https://www.googleapis.com/youtube/v3/videos"
        video_params = {
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": settings.YOUTUBE_API_KEY
        }
        
        video_res = requests.get(video_url, params=video_params)
        if video_res.status_code != 200:
            return []
            
        video_data = video_res.json()
        
        results = []
        for item in video_data.get("items", []):
            duration_iso = item["contentDetails"]["duration"]
            duration_sec = isodate.parse_duration(duration_iso).total_seconds()
            duration_hours = duration_sec / 3600.0
            
            results.append({
                "video_id": item["id"],
                "title": item["snippet"]["title"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "channel_id": item["snippet"]["channelId"],
                "published_at": item["snippet"]["publishedAt"],
                "duration_seconds": duration_sec,
                "duration_hours": duration_hours,
                "view_count": int(item["statistics"].get("viewCount", 0)),
                "quality_score": min((int(item["statistics"].get("likeCount", 0)) / (int(item["statistics"].get("viewCount", 1)) + 1)) * 100, 10.0) # Basic engagement metric
            })
            
        return results
        
    except Exception as e:
        print(f"Error calling YouTube API: {e}")
        return []
