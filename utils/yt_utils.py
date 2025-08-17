# This file provides utility functions for managing YouTube-related tasks.

import aiohttp
import asyncio
from typing import List, Dict, Any

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

async def fetch_youtube_data(api_key: str, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{YOUTUBE_API_URL}/{endpoint}", params={**params, 'key': api_key}) as response:
            return await response.json()

async def get_channel_videos(api_key: str, channel_id: str) -> List[Dict[str, Any]]:
    params = {
        'part': 'snippet',
        'channelId': channel_id,
        'maxResults': 50,
        'order': 'date'
    }
    data = await fetch_youtube_data(api_key, 'search', params)
    return data.get('items', [])

def extract_video_info(video_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': video_data['snippet']['title'],
        'url': f"https://www.youtube.com/watch?v={video_data['id']['videoId']}",
        'published_at': video_data['snippet']['publishedAt']
    }

async def get_latest_video(api_key: str, channel_id: str) -> Dict[str, Any]:
    videos = await get_channel_videos(api_key, channel_id)
    if videos:
        return extract_video_info(videos[0])
    return {}