"""
Simple download server for serving files to users
"""

import os
import hashlib
import asyncio
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Store active downloads
active_downloads: Dict[str, dict] = {}

def generate_download_token(file_path: str, user_id: int) -> str:
    """Generate unique token for file download"""
    token_data = f"{file_path}{user_id}{os.path.getsize(file_path)}{datetime.now()}"
    token = hashlib.md5(token_data.encode()).hexdigest()[:16]
    
    active_downloads[token] = {
        'file_path': file_path,
        'user_id': user_id,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(minutes=10)
    }
    
    return token

def get_download_link(token: str, bot_url: str = "http://localhost:8080") -> Optional[str]:
    """Get download URL for token"""
    if token in active_downloads:
        if datetime.now() < active_downloads[token]['expires_at']:
            return f"{bot_url}/download/{token}"
        else:
            # Cleanup expired token
            cleanup_token(token)
    return None

def get_file_path(token: str) -> Optional[str]:
    """Get file path from token"""
    if token in active_downloads:
        if datetime.now() < active_downloads[token]['expires_at']:
            return active_downloads[token]['file_path']
        else:
            cleanup_token(token)
    return None

def cleanup_token(token: str):
    """Remove token and delete file"""
    if token in active_downloads:
        file_path = active_downloads[token]['file_path']
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
        finally:
            del active_downloads[token]

async def cleanup_expired_files():
    """Background task to clean up expired files"""
    while True:
        await asyncio.sleep(60)  # Check every minute
        now = datetime.now()
        expired_tokens = []
        
        for token, data in active_downloads.items():
            if now > data['expires_at']:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            cleanup_token(token)
            logger.info(f"Cleaned up expired token: {token}")