"""
View for resolution selection dropdown - Complete Working Version with URL Encoding
"""

import discord
from discord import ui
import asyncio
import os
import uuid
import urllib.parse
import socket

class ResolutionView(ui.View):
    """View with resolution dropdown"""
    
    def __init__(self, url: str, formats: list, user_id: int):
        super().__init__(timeout=120)
        self.url = url
        self.formats = formats
        self.user_id = user_id
        self.message = None
        self.add_item(ResolutionDropdown(url, formats, user_id))
    
    async def on_timeout(self):
        if self.message:
            embed = discord.Embed(
                title="⏰ Session Expired",
                description="Please run /download again",
                color=discord.Color.orange()
            )
            await self.message.edit(embed=embed, view=None)

class ResolutionDropdown(ui.Select):
    """Dropdown for selecting resolution"""
    
    def __init__(self, url: str, formats: list, user_id: int):
        self.url = url
        self.user_id = user_id
        
        options = []
        for f in formats[:25]:
            size_text = f" ({f['filesize_mb']:.1f} MB)" if f['filesize_mb'] > 0 else ""
            options.append(
                discord.SelectOption(
                    label=f"{f['resolution']}{size_text}",
                    description=f"{f.get('format_note', 'Video')[:50]}",
                    value=f['format_id'],
                    emoji="🎬"
                )
            )
        
        super().__init__(
            placeholder="Choose video quality...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Not your menu!", ephemeral=True)
            return
        
        selected_id = self.values[0]
        
        selected = None
        for f in self.view.formats:
            if f['format_id'] == selected_id:
                selected = f
                break
        
        self.disabled = True
        await interaction.response.edit_message(view=self.view)
        
        # Progress embed
        progress_embed = discord.Embed(
            title="📥 Downloading Video",
            description="```\n[░░░░░░░░░░░░░░░░░░░░] 0%\n```\n🔄 Starting download...",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send("⏳ Processing...", ephemeral=True)
        progress_msg = await interaction.followup.send(
            embed=progress_embed,
            ephemeral=True,
            wait=True
        )
        
        async def update_progress(stage: str, percentage: int = 0):
            if stage == "downloading":
                bar_length = 20
                filled = int(bar_length * percentage / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                embed = discord.Embed(
                    title="📥 Downloading Video",
                    description=f"```\n[{bar}] {percentage}%\n```\n⏳ Downloading...",
                    color=discord.Color.blue()
                )
                await progress_msg.edit(embed=embed)
            elif stage == "processing":
                embed = discord.Embed(
                    title="📥 Downloading Video",
                    description="```\n[████████████████████] 100%\n```\n✅ Processing...",
                    color=discord.Color.green()
                )
                await progress_msg.edit(embed=embed)
        
        try:
            from utils.downloader import download_video
            
            # Update to show downloading
            await update_progress("downloading", 10)
            
            # Download video
            file_path, filename, file_size = await download_video(
                self.url,
                selected_id,
                update_progress,
                500  # 500MB max
            )
            
            await update_progress("processing", 100)
            
            file_size_mb = file_size / (1024 * 1024)
            
            # Get local IP
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            
            # ENCODE FILENAME FOR URL (Fix for spaces and special characters)
            encoded_filename = urllib.parse.quote(filename)
            
            # Generate download links with encoded filename
            local_url = f"http://localhost:8080/downloads/{encoded_filename}"
            network_url = f"http://{local_ip}:8080/downloads/{encoded_filename}"
            
            # Also create a direct file list URL
            file_list_url = f"http://localhost:8080"
            
            complete_embed = discord.Embed(
                title="✅ Download Complete!",
                description=f"**Video:** {filename}\n**Size:** {file_size_mb:.2f} MB\n**Quality:** {selected['resolution']}",
                color=discord.Color.green()
            )
            
            complete_embed.add_field(
                name="📥 Download Links",
                value=f"**On this PC (Click to download):**\n{local_url}\n\n**On Network (Other devices):**\n{network_url}\n\n**📁 All Files:**\n{file_list_url}\n\n*Click link to download*\n*File will be deleted after 10 minutes*",
                inline=False
            )
            
            complete_embed.add_field(
                name="💡 Tip",
                value="If link doesn't work, visit the 'All Files' link above and click on your video from the list.",
                inline=False
            )
            
            await progress_msg.edit(embed=complete_embed)
            
            # Auto-delete after 10 minutes
            async def delete_later():
                await asyncio.sleep(600)  # 10 minutes
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"🗑️ Deleted: {filename}")
            
            asyncio.create_task(delete_later())
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Download Failed",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
            await progress_msg.edit(embed=error_embed)