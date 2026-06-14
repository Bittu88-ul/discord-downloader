"""
Cleanup utilities for temporary files
Automatically deletes old downloaded files
"""

import os
import asyncio
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CleanupManager:
    """Manages automatic cleanup of temporary files"""
    
    def __init__(self, config: dict):
        """
        Initialize cleanup manager
        
        Args:
            config: Bot configuration dictionary
        """
        self.config = config
        self.retention_hours = config.get('TEMP_FILE_RETENTION_HOURS', 24)
        self.downloads_dir = Path("downloads")
        self.temp_dir = Path("temp")
        
    async def start_cleanup_scheduler(self):
        """Start background task that runs cleanup periodically"""
        logger.info(f"Starting cleanup scheduler (retention: {self.retention_hours} hours)")
        
        while True:
            try:
                await self.cleanup_old_files()
                # Run cleanup every 6 hours
                await asyncio.sleep(6 * 3600)
            except Exception as e:
                logger.error(f"Cleanup scheduler error: {e}")
                await asyncio.sleep(3600)  # Retry after 1 hour on error
    
    async def cleanup_old_files(self):
        """Delete files older than retention period"""
        try:
            now = time.time()
            retention_seconds = self.retention_hours * 3600
            deleted_count = 0
            
            # Clean downloads directory
            if self.downloads_dir.exists():
                for file_path in self.downloads_dir.iterdir():
                    if file_path.is_file():
                        file_age = now - file_path.stat().st_mtime
                        if file_age > retention_seconds:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.debug(f"Deleted old file: {file_path}")
            
            # Clean temp directory
            if self.temp_dir.exists():
                for file_path in self.temp_dir.iterdir():
                    if file_path.is_file():
                        file_age = now - file_path.stat().st_mtime
                        if file_age > retention_seconds:
                            os.remove(file_path)
                            deleted_count += 1
                            logger.debug(f"Deleted old temp file: {file_path}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup complete: deleted {deleted_count} old file(s)")
            else:
                logger.debug("Cleanup complete: no files to delete")
                
        except Exception as e:
            logger.error(f"Failed to cleanup files: {e}")
    
    def cleanup_sync(self):
        """Synchronous cleanup for immediate use"""
        try:
            now = time.time()
            retention_seconds = self.retention_hours * 3600
            
            for directory in [self.downloads_dir, self.temp_dir]:
                if directory.exists():
                    for file_path in directory.iterdir():
                        if file_path.is_file():
                            file_age = now - file_path.stat().st_mtime
                            if file_age > retention_seconds:
                                os.remove(file_path)
                                logger.debug(f"Deleted old file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup files: {e}")
    
    async def cleanup_single_file(self, file_path: str):
        """
        Immediately delete a specific file
        
        Args:
            file_path: Path to file to delete
        """
        try:
            path = Path(file_path)
            if path.exists():
                os.remove(path)
                logger.debug(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")