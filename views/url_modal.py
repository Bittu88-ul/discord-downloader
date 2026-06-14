"""
Discord Modal for URL input
Handles video URL submission and validation
"""

import discord
from discord import ui
from utils.validators import validate_url
from views.resolution_view import ResolutionView

class URLModal(ui.Modal, title="📥 Download Video"):
    """Modal for entering video URL"""
    
    url_input = ui.TextInput(
        label="Video URL",
        placeholder="https://www.youtube.com/watch?v=...",
        style=discord.TextStyle.short,
        required=True,
        min_length=10,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        await interaction.response.defer(ephemeral=True)
        
        url = self.url_input.value.strip()
        
        # Validate URL
        is_valid, message = validate_url(url)
        
        if not is_valid:
            embed = discord.Embed(
                title="❌ Invalid URL",
                description=message,
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Show processing message
        processing_embed = discord.Embed(
            title="🔍 Fetching Video Information",
            description="Please wait while I fetch available resolutions...",
            color=discord.Color.blue()
        )
        processing_msg = await interaction.followup.send(
            embed=processing_embed,
            ephemeral=True,
            wait=True
        )
        
        # Get available formats
        from utils.downloader import get_available_formats
        
        try:
            formats = await get_available_formats(url)
            
            if not formats:
                error_embed = discord.Embed(
                    title="❌ No Formats Found",
                    description="No downloadable formats found for this video.",
                    color=discord.Color.red()
                )
                await processing_msg.edit(embed=error_embed)
                return
            
            # Create view with resolution dropdown
            view = ResolutionView(url, formats, interaction.user.id)
            
            # Update message with dropdown
            select_embed = discord.Embed(
                title="🎬 Select Video Quality",
                description="Choose the resolution you want to download:",
                color=discord.Color.green()
            )
            
            # Add format info
            format_info = "\n".join([f"• **{f['resolution']}** - {f['format_note']}" for f in formats[:5]])
            if len(formats) > 5:
                format_info += f"\n*... and {len(formats) - 5} more formats*"
            
            select_embed.add_field(name="Available Formats", value=format_info, inline=False)
            
            await processing_msg.edit(
                embed=select_embed,
                view=view
            )
            view.message = processing_msg
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error Fetching Video",
                description=f"Failed to fetch video information: {str(e)}",
                color=discord.Color.red()
            )
            await processing_msg.edit(embed=error_embed)
    
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Handle modal errors"""
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=10)