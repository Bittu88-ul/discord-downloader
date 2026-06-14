#!/usr/bin/env python3
"""
Discord Video Downloader Bot
Main entry point for the bot application
"""

import discord
import os
from discord.ext import commands
import asyncio
import logging
import json
import sys
from pathlib import Path

os.makedirs("logs", exist_ok=True)

# Import utility modules
from utils.cleanup import CleanupManager
from views.url_modal import URLModal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

class VideoDownloaderBot(commands.Bot):
    """Main bot class for video downloader"""
    
    def __init__(self):
        """Initialize bot with command prefix and intents"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',  # Fallback prefix, main interface is slash commands
            intents=intents,
            help_command=None  # We'll implement custom help
        )
        
        self.config = config
        self.cleanup_manager = CleanupManager(config)
        
    async def setup_hook(self):
        """Called when bot is setting up - sync commands and start cleanup"""
        logger.info("Starting setup hook...")
        
        # Start background cleanup task
        self.loop.create_task(self.cleanup_manager.start_cleanup_scheduler())
        
        # Sync slash commands
        await self.sync_commands()
        
        logger.info("Setup hook completed")
    
    async def sync_commands(self):
        """Sync slash commands with Discord"""
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"Bot is in {len(self.guilds)} guild(s)")
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/download | Video Downloader"
            ),
            status=discord.Status.online
        )
        
        # Create necessary directories
        Path("downloads").mkdir(exist_ok=True)
        Path("temp").mkdir(exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
        
        logger.info("Bot is ready!")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        logger.error(f"Command error: {error}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    async def on_error(self, event_method, *args, **kwargs):
        """Handle general errors"""
        logger.error(f"Error in {event_method}: {sys.exc_info()}")

# Initialize bot
bot = VideoDownloaderBot()

@bot.tree.command(name="download", description="Download a video from supported platforms")
async def download_command(interaction: discord.Interaction):
    """Slash command to initiate video download"""
    logger.info(f"Download command used by {interaction.user.name} (ID: {interaction.user.id})")
    
    # Create and send modal for URL input
    modal = URLModal()
    await interaction.response.send_modal(modal)

def main():
    """Main entry point"""
    try:
        # Validate token
        if config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
            logger.error("Please set your bot token in config.json")
            sys.exit(1)
        
        # Run bot
        bot.run(config['BOT_TOKEN'])
    except discord.LoginFailure:
        logger.error("Invalid bot token provided")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()