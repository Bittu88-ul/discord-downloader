"""
URL validation utilities
Checks if URLs are valid and from supported platforms
"""

import re
from urllib.parse import urlparse
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

SUPPORTED_DOMAINS = config.get('ALLOWED_DOMAINS', [])

def validate_url(url: str) -> tuple:
    """
    Validate video URL
    
    Args:
        url: URL to validate
        
    Returns:
        Tuple of (is_valid, message)
    """
    # Check if URL is empty
    if not url or not url.strip():
        return False, "URL cannot be empty."
    
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Invalid URL format. Please include http:// or https://"
    
    # Parse URL
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain is supported
        is_supported = False
        for supported in SUPPORTED_DOMAINS:
            if supported in domain or domain in supported:
                is_supported = True
                break
        
        if not is_supported:
            supported_list = ", ".join(SUPPORTED_DOMAINS)
            return False, f"Unsupported website. Supported platforms: {supported_list}"
        
        return True, "URL is valid"
        
    except Exception as e:
        return False, f"URL parsing error: {str(e)}"

def get_supported_sites() -> list:
    """Get list of supported websites"""
    return SUPPORTED_DOMAINS

def is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube"""
    youtube_domains = ['youtube.com', 'youtu.be']
    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace('www.', '')
    return any(yt in domain for yt in youtube_domains)