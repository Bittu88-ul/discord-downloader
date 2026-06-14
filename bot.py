#!/usr/bin/env python3
"""
Discord Video Downloader Bot
Main entry point for the bot application - RENDER DEPLOYMENT READY
"""

import discord
import os
from discord.ext import commands
import asyncio
import logging
import json
import sys
from pathlib import Path

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("downloads", exist_ok=True)
os.makedirs("temp", exist_ok=True)

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

# ============================================
# LOAD CONFIGURATION - RENDER COMPATIBLE
# ============================================
def load_config():
    """Load config from environment variable or config.json"""
    config = {}
    
    # Try to get token from environment variable (Render.com)
    token = os.getenv('DISCORD_TOKEN')
    
    if token:
        logger.info("✅ Token loaded from environment variable")
        config['BOT_TOKEN'] = token
    else:
        # Fallback to config.json (local development)
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            logger.info("✅ Token loaded from config.json")
        except FileNotFoundError:
            logger.error("❌ No DISCORD_TOKEN found in environment variables or config.json")
            logger.error("Please set DISCORD_TOKEN in Render environment variables")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error("❌ config.json is malformed")
            sys.exit(1)
    
    return config

# Load configuration
config = load_config()

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
        self.cleanup_manager = CleanupManager(config) if 'cleanup' in config else None
        
    async def setup_hook(self):
        """Called when bot is setting up - sync commands and start cleanup"""
        logger.info("Starting setup hook...")
        
        # Start background cleanup task if cleanup manager exists
        if self.cleanup_manager:
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
        logger.info(f"✅ Logged in as {self.user.name} (ID: {self.user.id})")
        logger.info(f"📊 Bot is in {len(self.guilds)} guild(s)")
        
        # Set status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/download | Video Downloader"
            ),
            status=discord.Status.online
        )
        
        logger.info("🎉 Bot is ready to download videos!")
    
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
        if not config.get('BOT_TOKEN') or config['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
            logger.error("❌ Please set your bot token in config.json or DISCORD_TOKEN environment variable")
            sys.exit(1)
        
        # Run bot
        logger.info("🚀 Starting bot...")
        bot.run(config['BOT_TOKEN'])
    except discord.LoginFailure:
        logger.error("❌ Invalid bot token provided")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
