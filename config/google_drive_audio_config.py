#!/usr/bin/env python3
"""
Google Drive Audio Configuration
Maps audio files from the provided Google Drive folder to video scenes
"""

# Google Drive folder shared by user: https://drive.google.com/drive/folders/1XI7PRQn2jOgR0g52-3DAESFbXwVbkWks?usp=sharing
GOOGLE_DRIVE_AUDIO_FOLDER_ID = "1XI7PRQn2jOgR0g52-3DAESFbXwVbkWks"

# Base URL for Google Drive direct download
GOOGLE_DRIVE_DOWNLOAD_BASE = "https://drive.google.com/uc?export=download&id="

# Audio file mapping (to be updated with actual file IDs from the shared folder)
# Note: These are placeholder IDs and should be updated with actual file IDs from the folder
AUDIO_FILE_MAPPING = {
    'intro': {
        'file_id': 'https://drive.google.com/file/d/11j3rzom_mArLsQLLcEdS72y1W1qfvexG/view?usp=drive_link',
        'description': 'Intro voice narration',
        'duration_target': '5 seconds'
    },
    'product_1': {
        'file_id': 'https://drive.google.com/file/d/1mRK7aa3SmDfoCrrW9vcVhk_JgMgxOzO3/view?usp=drive_link', 
        'description': 'Product 1 voice narration',
        'duration_target': '9 seconds'
    },
    'product_2': {
        'file_id': 'https://drive.google.com/file/d/1YZMkkFOHf6MgIfuFKGlRY203lFnOF9lx/view?usp=drive_link',
        'description': 'Product 2 voice narration', 
        'duration_target': '9 seconds'
    },
    'product_3': {
        'file_id': 'https://drive.google.com/file/d/1B3xr17ewSEIXuZfMM19u5GkTYIVa5277/view?usp=drive_link',
        'description': 'Product 3 voice narration',
        'duration_target': '9 seconds'
    },
    'product_4': {
        'file_id': 'https://drive.google.com/file/d/14rsyWe_TsqkSKg9uHUvGyGzIVWW4np-_/view?usp=drive_link',
        'description': 'Product 4 voice narration',
        'duration_target': '9 seconds'
    },
    'product_5': {
        'file_id': 'https://drive.google.com/file/d/1cDF0io8VsvTXuaKaQYU02iHabrtvQsx5/view?usp=drive_link',
        'description': 'Product 5 voice narration',
        'duration_target': '9 seconds'
    },
    'outro': {
        'file_id': 'https://drive.google.com/file/d/1iib7wmnMrmRlXJ73Td-IOCpT0oKEVQGf/view?usp=drive_link',
        'description': 'Outro voice narration',
        'duration_target': '5 seconds'
    }
}

def get_audio_url(audio_type: str) -> str:
    """
    Get the direct download URL for a specific audio type
    
    Args:
        audio_type: One of 'intro', 'product_1', 'product_2', 'product_3', 'product_4', 'product_5', 'outro'
    
    Returns:
        Direct download URL for the audio file
    """
    if audio_type not in AUDIO_FILE_MAPPING:
        raise ValueError(f"Unknown audio type: {audio_type}. Available types: {list(AUDIO_FILE_MAPPING.keys())}")
    
    file_link = AUDIO_FILE_MAPPING[audio_type]['file_id']
    
    if file_link.startswith('UPDATE_WITH_ACTUAL'):
        # Return fallback URL if file ID hasn't been updated
        return "https://www.learningcontainer.com/wp-content/uploads/2020/02/Kalimba.mp3"
    
    # Extract file ID from Google Drive link
    if 'drive.google.com/file/d/' in file_link:
        # Extract file ID from URL like: https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
        file_id = file_link.split('/file/d/')[1].split('/')[0]
        print(f"🎵 Extracted file ID for {audio_type}: {file_id}")
        return f"{GOOGLE_DRIVE_DOWNLOAD_BASE}{file_id}"
    else:
        # Assume it's already a file ID
        return f"{GOOGLE_DRIVE_DOWNLOAD_BASE}{file_link}"

def get_all_audio_urls() -> dict:
    """Get all audio URLs mapped by type"""
    return {audio_type: get_audio_url(audio_type) for audio_type in AUDIO_FILE_MAPPING.keys()}

def validate_audio_url(url: str) -> bool:
    """
    Validate if an audio URL is accessible
    
    Args:
        url: Audio URL to validate
        
    Returns:
        True if URL appears valid, False otherwise
    """
    import requests
    try:
        # Make a HEAD request to check if URL is accessible
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def get_audio_validation_report() -> dict:
    """
    Generate a validation report for all configured audio URLs
    
    Returns:
        Dictionary with validation results for each audio type
    """
    report = {
        'folder_id': GOOGLE_DRIVE_AUDIO_FOLDER_ID,
        'total_files': len(AUDIO_FILE_MAPPING),
        'validation_results': {},
        'valid_count': 0,
        'invalid_count': 0
    }
    
    for audio_type in AUDIO_FILE_MAPPING.keys():
        url = get_audio_url(audio_type)
        is_valid = validate_audio_url(url)
        
        report['validation_results'][audio_type] = {
            'url': url,
            'is_valid': is_valid,
            'description': AUDIO_FILE_MAPPING[audio_type]['description'],
            'duration_target': AUDIO_FILE_MAPPING[audio_type]['duration_target']
        }
        
        if is_valid:
            report['valid_count'] += 1
        else:
            report['invalid_count'] += 1
    
    report['overall_status'] = 'valid' if report['invalid_count'] == 0 else 'needs_attention'
    
    return report

# Instructions for updating file IDs
INSTRUCTIONS = """
To update this configuration with actual file IDs from your Google Drive folder:

1. Open the shared folder: https://drive.google.com/drive/folders/1XI7PRQn2jOgR0g52-3DAESFbXwVbkWks?usp=sharing

2. For each audio file, right-click and select "Get link" 

3. The link will look like: https://drive.google.com/file/d/FILE_ID_HERE/view?usp=sharing

4. Extract the FILE_ID_HERE part and update the corresponding entry in AUDIO_FILE_MAPPING

5. Ensure all files are set to "Anyone with the link can view" for public access

Example:
If you have a file with link: https://drive.google.com/file/d/1ABC123XYZ789/view?usp=sharing
Update the file_id to: '1ABC123XYZ789'
"""

if __name__ == "__main__":
    print("🎵 Google Drive Audio Configuration")
    print("=" * 50)
    print(f"📁 Folder ID: {GOOGLE_DRIVE_AUDIO_FOLDER_ID}")
    print(f"🔗 Folder URL: https://drive.google.com/drive/folders/{GOOGLE_DRIVE_AUDIO_FOLDER_ID}")
    print(f"📊 Configured audio files: {len(AUDIO_FILE_MAPPING)}")
    
    print("\n📋 Audio File Mapping:")
    for audio_type, config in AUDIO_FILE_MAPPING.items():
        print(f"   {audio_type}: {config['description']} ({config['duration_target']})")
    
    print(f"\n{INSTRUCTIONS}")
    
    # Generate validation report
    print("\n🔍 Validation Report:")
    report = get_audio_validation_report()
    print(f"Overall Status: {report['overall_status']}")
    print(f"Valid URLs: {report['valid_count']}/{report['total_files']}")
    
    if report['invalid_count'] > 0:
        print("\n❌ Invalid URLs:")
        for audio_type, result in report['validation_results'].items():
            if not result['is_valid']:
                print(f"   {audio_type}: {result['description']}")