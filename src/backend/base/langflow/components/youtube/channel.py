from typing import Dict, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langflow.custom import Component
from langflow.inputs import BoolInput, MessageTextInput, SecretStrInput
from langflow.schema import Data
from langflow.template import Output

class YouTubeChannelComponent(Component):
    """A component that retrieves detailed information about YouTube channels."""
    
    display_name: str = "YouTube Channel"
    description: str = "Retrieves detailed information and statistics about YouTube channels."
    icon: str = "YouTube"
    name = "YouTubeChannel"

    inputs = [
        MessageTextInput(
            name="channel_url",
            display_name="Channel URL or ID",
            info="The URL or ID of the YouTube channel.",
            tool_mode=True,
        ),
        SecretStrInput(
            name="api_key",
            display_name="YouTube API Key",
            info="Your YouTube Data API key.",
            required=True,
        ),
        BoolInput(
            name="include_statistics",
            display_name="Include Statistics",
            value=True,
            info="Include channel statistics (views, subscribers, videos).",
        ),
        BoolInput(
            name="include_branding",
            display_name="Include Branding",
            value=True,
            info="Include channel branding settings (banner, thumbnails).",
            advanced=True,
        ),
        BoolInput(
            name="include_playlists",
            display_name="Include Playlists",
            value=False,
            info="Include channel's public playlists.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(name="channel_data", display_name="Channel Data", method="get_channel_info"),
    ]

    def _extract_channel_id(self, channel_url: str) -> str:
        """
        Extracts the channel ID from various YouTube channel URL formats.
        
        Args:
            channel_url (str): The URL or ID of the YouTube channel
            
        Returns:
            str: The channel ID
        """
        import re

        # If it's already a channel ID (starts with UC)
        if channel_url.startswith('UC') and len(channel_url) == 24:
            return channel_url

        # Different URL patterns
        patterns = {
            'custom_url': r'youtube\.com\/c\/([^\/\n?]+)',
            'channel_id': r'youtube\.com\/channel\/([^\/\n?]+)',
            'user': r'youtube\.com\/user\/([^\/\n?]+)',
            'handle': r'youtube\.com\/@([^\/\n?]+)',
        }

        for pattern_type, pattern in patterns.items():
            match = re.search(pattern, channel_url)
            if match:
                if pattern_type == 'channel_id':
                    return match.group(1)
                else:
                    # Need to make an API call to get the channel ID
                    return self._get_channel_id_by_name(match.group(1), pattern_type)

        # If no patterns match, return the input as is
        return channel_url

    def _get_channel_id_by_name(self, channel_name: str, identifier_type: str) -> str:
        """
        Gets the channel ID using the channel name or custom URL.
        
        Args:
            channel_name (str): The channel name or custom URL
            identifier_type (str): The type of identifier ('custom_url', 'user', or 'handle')
            
        Returns:
            str: The channel ID
        """
        try:
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            if identifier_type == 'handle':
                # Remove @ from handle
                channel_name = channel_name.lstrip('@')
                
            # Search for the channel
            request = youtube.search().list(
                part="id",
                q=channel_name,
                type="channel",
                maxResults=1
            )
            response = request.execute()

            if response['items']:
                return response['items'][0]['id']['channelId']
            else:
                raise ValueError(f"Could not find channel ID for: {channel_name}")

        except Exception as e:
            raise ValueError(f"Error getting channel ID: {str(e)}")

    def _get_channel_playlists(self, youtube: any, channel_id: str, max_results: int = 10) -> list:
        """
        Gets the public playlists for a channel.
        
        Args:
            youtube: YouTube API client
            channel_id (str): The channel ID
            max_results (int): Maximum number of playlists to return
            
        Returns:
            list: List of playlist information
        """
        try:
            playlists_request = youtube.playlists().list(
                part="snippet,contentDetails",
                channelId=channel_id,
                maxResults=max_results
            )
            playlists_response = playlists_request.execute()

            playlists = []
            for item in playlists_response.get('items', []):
                playlist_data = {
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'playlist_id': item['id'],
                    'video_count': item['contentDetails']['itemCount'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnail_url': item['snippet']['thumbnails']['default']['url']
                }
                playlists.append(playlist_data)

            return playlists

        except Exception as e:
            return [{'error': f"Error fetching playlists: {str(e)}"}]

    def get_channel_info(self) -> Data:
        """
        Retrieves detailed information about a YouTube channel.
        
        Returns:
            Data: A Data object containing channel information
        """
        try:
            # Extract channel ID from URL
            channel_id = self._extract_channel_id(self.channel_url)
            
            # Initialize YouTube API client
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Prepare parts for the API request
            parts = ['snippet', 'contentDetails']
            if self.include_statistics:
                parts.append('statistics')
            if self.include_branding:
                parts.append('brandingSettings')

            # Get channel information
            channel_response = youtube.channels().list(
                part=','.join(parts),
                id=channel_id
            ).execute()

            if not channel_response['items']:
                return Data(data={"error": "Channel not found"})

            channel_info = channel_response['items'][0]
            
            # Build basic channel data
            channel_data = {
                "title": channel_info['snippet']['title'],
                "description": channel_info['snippet']['description'],
                "custom_url": channel_info['snippet'].get('customUrl', ''),
                "published_at": channel_info['snippet']['publishedAt'],
                "thumbnails": {
                    size: thumb['url']
                    for size, thumb in channel_info['snippet']['thumbnails'].items()
                },
                "country": channel_info['snippet'].get('country', 'Not specified'),
                "channel_id": channel_id,
            }

            # Add statistics if requested
            if self.include_statistics:
                stats = channel_info['statistics']
                channel_data["statistics"] = {
                    "view_count": int(stats.get('viewCount', 0)),
                    "subscriber_count": int(stats.get('subscriberCount', 0)),
                    "hidden_subscriber_count": stats.get('hiddenSubscriberCount', False),
                    "video_count": int(stats.get('videoCount', 0)),
                }

            # Add branding information if requested
            if self.include_branding:
                branding = channel_info.get('brandingSettings', {})
                channel_data["branding"] = {
                    "title": branding.get('channel', {}).get('title', ''),
                    "description": branding.get('channel', {}).get('description', ''),
                    "keywords": branding.get('channel', {}).get('keywords', ''),
                    "banner_url": branding.get('image', {}).get('bannerExternalUrl', ''),
                }

            # Add playlists if requested
            if self.include_playlists:
                channel_data["playlists"] = self._get_channel_playlists(youtube, channel_id)

            self.status = channel_data
            return Data(data=channel_data)

        except HttpError as e:
            error_message = f"YouTube API error: {str(e)}"
            if e.resp.status == 403:
                error_message = "API quota exceeded or access forbidden."
            elif e.resp.status == 404:
                error_message = "Channel not found."
                
            error_data = {"error": error_message}
            self.status = error_data
            return Data(data=error_data)
            
        except Exception as e:
            error_data = {"error": f"An error occurred: {str(e)}"}
            self.status = error_data
            return Data(data=error_data)