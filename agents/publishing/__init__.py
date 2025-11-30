"""
Publishing Agent
=================
Handles publishing to all platforms (YouTube, WordPress, Instagram).
"""

from .agent import PublishingAgent
from .youtube_publisher_subagent import YouTubePublisherSubAgent
from .wordpress_publisher_subagent import WordPressPublisherSubAgent
from .instagram_publisher_subagent import InstagramPublisherSubAgent
from .airtable_updater_subagent import AirtableUpdaterSubAgent

__all__ = [
    'PublishingAgent',
    'YouTubePublisherSubAgent',
    'WordPressPublisherSubAgent',
    'InstagramPublisherSubAgent',
    'AirtableUpdaterSubAgent',
]
