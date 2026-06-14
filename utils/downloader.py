"""
Video downloading utilities - Fixed file finding
"""

import yt_dlp
import asyncio
import os
import uuid
import re
from pathlib import Path

async def get_available_formats(url: str) -> list:
    """Get available formats"""
    def sync_get():
        ydl_opts = {'quiet': True, 'no_warnings': True}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            seen = set()
            
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('height'):
                    height = f['height']
                    res = f"{height}p"
                    
                    if res not in seen:
                        seen.add(res)
                        size = f.get('filesize', 0) or f.get('filesize_approx', 0)
                        formats.append({
                            'format_id': f['format_id'],
                            'resolution': res,
                            'format_note': f.get('format_note', ''),
                            'filesize_mb': size / (1024 * 1024) if size else 0,
                        })
            
            formats.sort(key=lambda x: int(x['resolution'].replace('p', '')), reverse=True)
            return formats
    
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_get)

async def download_video(url: str, format_id: str, progress_callback, max_size_mb: int):
    """Download video and return file path"""
    unique_id = str(uuid.uuid4())[:8]
    
    # Create downloads directory if not exists
    os.makedirs('downloads', exist_ok=True)
    
    def sync_download():
        try:
            # Configure yt-dlp
            opts = {
                'quiet': True,
                'no_warnings': True,
                'format': format_id,
                'outtmpl': f'downloads/video_{unique_id}_%(title)s.%(ext)s',
                'restrictfilenames': True,
                'ignoreerrors': False,
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                # Download video
                info = ydl.extract_info(url, download=True)
                
                # Get the expected filename
                expected_filename = ydl.prepare_filename(info)
                
                print(f"Expected filename: {expected_filename}")
                
                # Check if file exists
                if os.path.exists(expected_filename):
                    return expected_filename, os.path.basename(expected_filename), os.path.getsize(expected_filename)
                
                # Try with different extensions
                base_name = os.path.splitext(expected_filename)[0]
                for ext in ['.mp4', '.webm', '.mkv', '.mp3']:
                    test_path = base_name + ext
                    if os.path.exists(test_path):
                        print(f"Found file with extension: {test_path}")
                        return test_path, os.path.basename(test_path), os.path.getsize(test_path)
                
                # Also check downloads directory for any file with our unique_id
                downloads_dir = 'downloads'
                if os.path.exists(downloads_dir):
                    for file in os.listdir(downloads_dir):
                        if unique_id in file:
                            file_path = os.path.join(downloads_dir, file)
                            print(f"Found file by unique_id: {file_path}")
                            return file_path, file, os.path.getsize(file_path)
                
                raise Exception(f"Downloaded file not found. Expected: {expected_filename}")
                
        except Exception as e:
            print(f"Download error: {e}")
            raise
    
    await progress_callback("downloading", 50)
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, sync_download)
    
    await progress_callback("processing", 100)
    return result