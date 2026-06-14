"""
Custom button components for the bot
(Reserved for future features like cancel, retry, etc.)
"""

import discord
from discord import ui

class CancelButton(ui.Button):
    """Cancel download button"""
    
    def __init__(self):
        super().__init__(
            label="Cancel",
            style=discord.ButtonStyle.danger,
            emoji="❌",
            custom_id="cancel_download"
        )
    
    async def callback(self, interaction: discord.Interaction):
        """Handle cancel button press"""
        # This will be implemented for cancellation feature
        embed = discord.Embed(
            title="❌ Cancelled",
            description="Download has been cancelled.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class RetryButton(ui.Button):
    """Retry download button"""
    
    def __init__(self, url: str, format_id: str):
        super().__init__(
            label="Retry",
            style=discord.ButtonStyle.primary,
            emoji="🔄",
            custom_id="retry_download"
        )
        self.url = url
        self.format_id = format_id
    
    async def callback(self, interaction: discord.Interaction):
        """Handle retry button press"""
        embed = discord.Embed(
            title="🔄 Retrying",
            description="Attempting to download again...",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        # Retry logic would go here