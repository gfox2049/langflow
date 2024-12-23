from typing import Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langflow.custom import Component
from langflow.inputs import IntInput, SecretStrInput, DropdownInput, BoolInput
from langflow.schema import Data
from langflow.template import Output

class YouTubeTrendingComponent(Component):
    """A component that retrieves trending videos from YouTube."""
    
    display_name: str = "YouTube Trending"
    description: str = "Retrieves trending videos from YouTube with filtering options."
    icon: str = "YouTube"
    name = "YouTubeTrending"

    # Dictionary of country codes and names
    COUNTRY_CODES = {
        "Global": "US",  # Default to US for global
        "United States": "US",
        "Brazil": "BR",
        "United Kingdom": "GB",
        "India": "IN",
        "Japan": "JP",
        "South Korea": "KR",
        "Germany": "DE",
        "France": "FR",
        "Canada": "CA",
        "Australia": "AU",
        "Spain": "ES",
        "Italy": "IT",
        "Mexico": "MX",
        "Russia": "RU",
        "Netherlands": "NL",
        "Poland": "PL",
        "Argentina": "AR",
    }

    # Dictionary of video categories
    VIDEO_CATEGORIES = {
        "All": "0",
        "Film & Animation": "1",
        "Autos & Vehicles": "2",
        "Music": "10",
        "Pets & Animals": "15",
        "Sports": "17",
        "Travel & Events": "19",
        "Gaming": "20",
        "People & Blogs": "22",
        "Comedy": "23",
        "Entertainment": "24",
        "News & Politics": "25",
        "Education": "27",
        "Science & Technology": "28",
        "Nonprofits & Activism": "29",
    }

    inputs = [
        SecretStrInput(
            name="api_key",
            display_name="YouTube API Key",
            info="Your YouTube Data API key.",
            required=True,
        ),
        DropdownInput(
            name="region",
            display_name="Region",
            options=list(COUNTRY_CODES.keys()),
            value="Global",
            info="The region to get trending videos from.",
        ),
        DropdownInput(
            name="category",
            display_name="Category",
            options=list(VIDEO_CATEGORIES.keys()),
            value="All",
            info="The category of videos to retrieve.",
        ),
        IntInput(
            name="max_results",
            display_name="Max Results",
            value=10,
            info="Maximum number of trending videos to return (1-50).",
        ),
        BoolInput(
            name="include_statistics",
            display_name="Include Statistics",
            value=True,
            info="Include video statistics (views, likes, comments).",
        ),
        BoolInput(
            name="include_content_details",
            display_name="Include Content Details",
            value=True,
            info="Include video duration and quality info.",
            advanced=True,
        ),
        BoolInput(
            name="include_thumbnails",
            display_name="Include Thumbnails",
            value=True,
            info="Include video thumbnail URLs.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(name="trending_videos", display_name="Trending Videos", method="get_trending_videos"),
    ]

    def _format_duration(self, duration: str) -> str:
        """Formats ISO 8601 duration to readable format."""
        import re
        import datetime

        # Remove 'PT' from the start of duration
        duration = duration[2:]
        
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours, minutes and seconds
        time_dict = {}
        for time_unit in ['H', 'M', 'S']:
            match = re.search(r'(\d+)' + time_unit, duration)
            if match:
                time_dict[time_unit] = int(match.group(1))
                
        if 'H' in time_dict:
            hours = time_dict['H']
        if 'M' in time_dict:
            minutes = time_dict['M']
        if 'S' in time_dict:
            seconds = time_dict['S']

        # Format the time string
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def get_trending_videos(self) -> List[Data]:
        """
        Retrieves trending videos from YouTube based on specified parameters.
        
        Returns:
            List[Data]: A list of Data objects containing trending video information
        """
        try:
            # Validate max_results
            if not 1 <= self.max_results <= 50:
                self.max_results = min(max(1, self.max_results), 50)

            # Build YouTube API client
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Get country code
            region_code = self.COUNTRY_CODES[self.region]
            
            # Prepare API request parts
            parts = ['snippet']
            if self.include_statistics:
                parts.append('statistics')
            if self.include_content_details:
                parts.append('contentDetails')
            
            # Prepare API request parameters
            request_params = {
                'part': ','.join(parts),
                'chart': 'mostPopular',
                'regionCode': region_code,
                'maxResults': self.max_results,
            }
            
            # Add category filter if not "All"
            if self.category != "All":
                request_params['videoCategoryId'] = self.VIDEO_CATEGORIES[self.category]
            
            # Get trending videos
            request = youtube.videos().list(**request_params)
            response = request.execute()
            
            trending_videos = []
            
            for item in response.get('items', []):
                video_data = {
                    "video_id": item['id'],
                    "title": item['snippet']['title'],
                    "description": item['snippet']['description'],
                    "channel_id": item['snippet']['channelId'],
                    "channel_title": item['snippet']['channelTitle'],
                    "published_at": item['snippet']['publishedAt'],
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                }
                
                # Add thumbnails if requested
                if self.include_thumbnails:
                    video_data["thumbnails"] = {
                        size: {
                            "url": thumb['url'],
                            "width": thumb.get('width', 0),
                            "height": thumb.get('height', 0)
                        }
                        for size, thumb in item['snippet']['thumbnails'].items()
                    }
                
                # Add statistics if requested
                if self.include_statistics and 'statistics' in item:
                    video_data["statistics"] = {
                        "view_count": int(item['statistics'].get('viewCount', 0)),
                        "like_count": int(item['statistics'].get('likeCount', 0)),
                        "comment_count": int(item['statistics'].get('commentCount', 0)),
                    }
                
                # Add content details if requested
                if self.include_content_details and 'contentDetails' in item:
                    content_details = item['contentDetails']
                    video_data["content_details"] = {
                        "duration": self._format_duration(content_details['duration']),
                        "definition": content_details.get('definition', 'hd').upper(),
                        "caption": content_details.get('caption', 'false') == 'true',
                        "licensed_content": content_details.get('licensedContent', False),
                        "projection": content_details.get('projection', 'rectangular'),
                    }
                
                trending_videos.append(Data(data=video_data))
            
            self.status = trending_videos
            return trending_videos

        except HttpError as e:
            error_message = f"YouTube API error: {str(e)}"
            if e.resp.status == 403:
                error_message = "API quota exceeded or access forbidden."
            elif e.resp.status == 404:
                error_message = "Resource not found."
                
            error_data = [Data(data={"error": error_message})]
            self.status = error_data
            return error_data
            
        except Exception as e:
            error_data = [Data(data={"error": f"An error occurred: {str(e)}"})]
            self.status = error_data
            return error_data