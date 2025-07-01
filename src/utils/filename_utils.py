import re
import logging

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Remove or replace problematic characters for Google Drive"""
    original = filename
    
    # Remove emojis and special unicode characters
    filename = re.sub(r'[^\x00-\x7F]+', '', filename)
    
    # Replace problematic punctuation
    replacements = {
        '|': '-',
        '\\': '-',
        '/': '-',
        ':': '-',
        '*': '',
        '?': '',
        '"': '',
        '<': '',
        '>': '',
        '!': ''
    }
    
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    # Clean up multiple spaces and hyphens
    filename = re.sub(r'\s+', ' ', filename)
    filename = re.sub(r'-+', '-', filename)
    
    # Remove leading/trailing spaces and hyphens
    filename = filename.strip(' -')
    
    # Ensure filename is not empty
    if not filename:
        filename = "Untitled"
    
    # Limit length to 255 characters
    if len(filename) > 255:
        filename = filename[:252] + "..."
    
    if original != filename:
        logger.info(f"Sanitized: '{original}' -> '{filename}'")
    
    return filename
