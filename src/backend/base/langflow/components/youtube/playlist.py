from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langflow.custom import Component
from langflow.inputs import IntInput, SecretStrInput, MessageTextInput, BoolInput, DropdownInput
from langflow.schema import Data
from langflow.template import Output

class YouTubePlaylistComponent(Component):
    """A component that retrieves and analyzes YouTube playlists."""
    
    display_name: str = "YouTube Playlist"
    description: str = "Retrieves and analyzes YouTube playlist information and videos."
    icon: str = "YouTube"
    name = "YouTubePlaylist"

    inputs = [
        MessageTextInput(
            name="playlist_url",
            display_name="Playlist URL or ID",
            info="The URL or ID of the YouTube playlist.",
            tool_mode=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="YouTube API Key",
            info="Your YouTube Data API key.",
            required=True,
        ),
        IntInput(
            name="max_videos",
            display_name="Max Videos",
            value=50,
            info="Maximum number of videos to retrieve from the playlist (1-500).",
        ),
        BoolInput(
            name="include_video_details",
            display_name="Include Video Details",
            value=True,
            info="Include detailed information about each video.",
        ),
        BoolInput(
            name="include_statistics",
            display_name="Include Statistics",
            value=True,
            info="Include playlist and video statistics.",
        ),
        DropdownInput(
            name="sort_order",
            display_name="Sort Order",
            options=["position", "date", "rating", "title"],
            value="position",
            info="Sort order for playlist videos.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(name="playlist_data", display_name="Playlist Data", method="get_playlist_info"),
    ]

    def _extract_playlist_id(self, playlist_url: str) -> str:
        """
        Extracts the playlist ID from various YouTube playlist URL formats.
        
        Args:
            playlist_url (str): The URL or ID of the YouTube playlist
            
        Returns:
            str: The playlist ID
        """
        import re
        
        # If it's already a playlist ID
        if playlist_url.startswith('PL') and len(playlist_url) > 12:
            return playlist_url
            
        # Regular expressions for different playlist URL formats
        patterns = [
            r'[?&]list=([^&\s]+)',  # Standard format
            r'youtube\.com/playlist\?.*list=([^&\s]+)',  # Playlist page
            r'youtube\.com/watch\?.*list=([^&\s]+)'  # Video in playlist
        ]
        
        for pattern in patterns:
            match = re.search(pattern, playlist_url)
            if match:
                return match.group(1)
        
        return playlist_url.strip()

    def _format_duration(self, duration: str) -> str:
        """
        Formats ISO 8601 duration to readable format.
        """
        import re
        
        # Remove PT from start
        duration = duration.replace('PT', '')
        
        # Initialize hours, minutes, seconds
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours, minutes, and seconds
        hours_match = re.search(r'(\d+)H', duration)
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)
        
        if hours_match:
            hours = int(hours_match.group(1))
        if minutes_match:
            minutes = int(minutes_match.group(1))
        if seconds_match:
            seconds = int(seconds_match.group(1))
        
        # Format output
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    def _sort_videos(self, videos: List[Dict], sort_order: str) -> List[Dict]:
        """
        Sorts the video list based on the specified order.
        """
        if sort_order == "position":
            return sorted(videos, key=lambda x: x.get('position', 0))
        elif sort_order == "date":
            return sorted(videos, key=lambda x: x.get('published_at', ''), reverse=True)
        elif sort_order == "rating":
            return sorted(videos, key=lambda x: (
                int(x.get('statistics', {}).get('like_count', 0)) if 'statistics' in x else 0
            ), reverse=True)
        elif sort_order == "title":
            return sorted(videos, key=lambda x: x.get('title', '').lower())
        return videos

    def get_playlist_info(self) -> Data:
        """
        Retrieves detailed information about a YouTube playlist and its videos.
        
        Returns:
            Data: A Data object containing playlist information and videos
        """
        try:
            # Extract playlist ID
            playlist_id = self._extract_playlist_id(self.playlist_url)
            
            # Initialize YouTube API client
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Get playlist details
            playlist_response = youtube.playlists().list(
                part="snippet,status,contentDetails,player",
                id=playlist_id
            ).execute()

            if not playlist_response['items']:
                return Data(data={"error": "Playlist not found"})

            playlist_info = playlist_response['items'][0]
            
            # Build basic playlist data
            playlist_data = {
                "playlist_id": playlist_id,
                "title": playlist_info['snippet']['title'],
                "description": playlist_info['snippet']['description'],
                "channel_id": playlist_info['snippet']['channelId'],
                "channel_title": playlist_info['snippet']['channelTitle'],
                "published_at": playlist_info['snippet']['publishedAt'],
                "privacy_status": playlist_info['status']['privacyStatus'],
                "video_count": playlist_info['contentDetails']['itemCount'],
                "thumbnails": playlist_info['snippet']['thumbnails'],
                "videos": []
            }

            # Get videos in playlist
            videos = []
            next_page_token = None
            total_videos = 0

            while total_videos < self.max_videos:
                # Get playlist items
                playlist_items = youtube.playlistItems().list(
                    part="snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=min(50, self.max_videos - total_videos),
                    pageToken=next_page_token
                ).execute()

                if not playlist_items.get('items'):
                    break

                video_ids = [item['contentDetails']['videoId'] for item in playlist_items['items']]
                
                # Get detailed video information if requested
                if self.include_video_details:
                    parts = ['snippet', 'contentDetails']
                    if self.include_statistics:
                        parts.append('statistics')
                        
                    video_response = youtube.videos().list(
                        part=','.join(parts),
                        id=','.join(video_ids)
                    ).execute()

                    # Map video details to playlist items
                    for playlist_item in playlist_items['items']:
                        video_id = playlist_item['contentDetails']['videoId']
                        video_info = next(
                            (v for v in video_response.get('items', []) if v['id'] == video_id), 
                            None
                        )
                        
                        if video_info:
                            video_data = {
                                "video_id": video_id,
                                "title": video_info['snippet']['title'],
                                "description": video_info['snippet']['description'],
                                "position": playlist_item['snippet']['position'],
                                "published_at": video_info['snippet']['publishedAt'],
                                "thumbnails": video_info['snippet']['thumbnails'],
                                "url": f"https://www.youtube.com/watch?v={video_id}",
                            }
                            
                            if 'contentDetails' in video_info:
                                video_data["duration"] = self._format_duration(
                                    video_info['contentDetails']['duration']
                                )
                            
                            if self.include_statistics and 'statistics' in video_info:
                                video_data["statistics"] = {
                                    "view_count": int(video_info['statistics'].get('viewCount', 0)),
                                    "like_count": int(video_info['statistics'].get('likeCount', 0)),
                                    "comment_count": int(video_info['statistics'].get('commentCount', 0)),
                                }
                                
                            videos.append(video_data)
                else:
                    # Basic video information from playlist items
                    for item in playlist_items['items']:
                        video_data = {
                            "video_id": item['contentDetails']['videoId'],
                            "title": item['snippet']['title'],
                            "description": item['snippet']['description'],
                            "position": item['snippet']['position'],
                            "published_at": item['snippet']['publishedAt'],
                            "thumbnails": item['snippet']['thumbnails'],
                            "url": f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}",
                        }
                        videos.append(video_data)

                total_videos += len(playlist_items['items'])
                next_page_token = playlist_items.get('nextPageToken')
                
                if not next_page_token:
                    break

            # Sort videos based on specified order
            videos = self._sort_videos(videos, self.sort_order)
            
            # Add sorted videos to playlist data
            playlist_data["videos"] = videos
            
            # Calculate total duration if video details were requested
            if self.include_video_details:
                total_seconds = 0
                for video in videos:
                    if "duration" in video:
                        parts = video["duration"].split(":")
                        if len(parts) == 2:  # MM:SS
                            total_seconds += int(parts[0]) * 60 + int(parts[1])
                        elif len(parts) == 3:  # HH:MM:SS
                            total_seconds += int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                playlist_data["total_duration"] = f"{hours}h {minutes}m"

            self.status = playlist_data
            return Data(data=playlist_data)

        except HttpError as e:
            error_message = f"YouTube API error: {str(e)}"
            if e.resp.status == 403:
                error_message = "API quota exceeded or access forbidden."
            elif e.resp.status == 404:
                error_message = "Playlist not found."
                
            error_data = {"error": error_message}
            self.status = error_data
            return Data(data=error_data)
            
        except Exception as e:
            error_data = {"error": f"An error occurred: {str(e)}"}
            self.status = error_data
            return Data(data=error_data)