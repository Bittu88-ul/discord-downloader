"""
Logging utilities for the bot
Handles logging successful downloads to configured channel
"""

import discord
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def log_download(client: discord.Client, user: discord.User, filename: str):
    """
    Log successful download to configured log channel
    
    Args:
        client: Discord client instance
        user: User who downloaded the video
        filename: Name of downloaded file
    """
    try:
        log_channel_id = client.config.get('LOG_CHANNEL_ID')
        
        if not log_channel_id:
            logger.warning("LOG_CHANNEL_ID not configured in config.json")
            return
        
        channel = client.get_channel(log_channel_id)
        
        if not channel:
            logger.warning(f"Log channel {log_channel_id} not found")
            return
        
        # Create log embed
        embed = discord.Embed(
            title="📥 Video Downloaded",
            description=f"**User:** {user.mention}\n**Username:** {user.name}\n**User ID:** {user.id}\n**Filename:** `{filename}`",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        # Add user avatar
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.set_footer(text=f"Download completed")
        
        await channel.send(embed=embed)
        logger.info(f"Logged download for {user.name}: {filename}")
        
    except Exception as e:
        logger.error(f"Failed to log download: {e}")

async def log_error(client: discord.Client, error: str, user: discord.User = None):
    """
    Log errors to log channel (optional)
    
    Args:
        client: Discord client instance
        error: Error message
        user: User who encountered the error (optional)
    """
    try:
        log_channel_id = client.config.get('LOG_CHANNEL_ID')
        
        if not log_channel_id:
            return
        
        channel = client.get_channel(log_channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="❌ Download Error",
            description=f"**Error:** {error}\n**User:** {user.mention if user else 'Unknown'}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        await channel.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Failed to log error: {e}")