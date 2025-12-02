# Google Drive Project Folder Structure Implementation

## Overview

Added project-specific folder level to Google Drive organization as requested.
Media files now organized by project title for easier management.

## New Folder Structure

### Before
```
ReviewCh3kr_Media/
├── Images/{RecordID}/
├── Audio/{RecordID}/
└── Videos/{RecordID}/
```

### After
```
ReviewCh3kr_Media/
└── {Project Title}/  (e.g., "Top 5 best gaming headphones 2025")
    ├── Images/{RecordID}/
    ├── Audio/{RecordID}/
    └── Videos/{RecordID}/
```

## Implementation Status

### ✅ Completed
1. **Google Drive Module** (`src/mcp/production_enhanced_google_drive_agent_mcp.py`)
   - Added `sanitize_folder_name()` function to clean project titles
   - Updated `_setup_folder_structure()` to create project folder level
   - Updated `upload_file()` to accept `project_title` parameter
   - Updated async wrapper to pass `project_title`

2. **DualStorageManager** (`src/utils/dual_storage_manager.py`)
   - Updated `save_media()` to accept `project_title` parameter
   - Updated `_upload_to_drive_async()` to pass `project_title`

3. **Image Generator SubAgent** (`agents/content_generation/image_generator_subagent.py`)
   - Updated `execute_task()` to extract `project_title` from task
   - Updated `_save_image()` to accept and pass `project_title`

4. **Voice Generator SubAgent** (`agents/content_generation/voice_generator_subagent.py`)
   - Updated `_generate_voice_file()` to accept and pass `project_title`

### ⏳ Remaining Work

1. **Voice Generator SubAgent** - Update execute_task and call sites
   - Update `execute_task()` to extract `project_title` from task
   - Update all calls to `_generate_voice_file()` to pass `project_title`

2. **WOW Video SubAgent** (`agents/video_production/wow_video_subagent.py`)
   - Update `execute_task()` to extract `project_title` from task
   - Update video upload to pass `project_title`

3. **Content Generation Parent Agent** (`agents/content_generation/agent.py`)
   - Extract `project_title` from fetch_title phase
   - Pass `project_title` to all image generation subagent calls
   - Pass `project_title` to voice generation subagent call

4. **Video Production Parent Agent** (`agents/video_production/agent.py`)
   - Pass `project_title` to video subagent

5. **Orchestrator** (`agents/orchestrator.py`)
   - Store `project_title` from Phase 1 (FETCH_TITLE)
   - Pass `project_title` to all content generation and video production phases

## Title Sanitization

The `sanitize_folder_name()` function ensures project titles are safe for Google Drive:
- Removes invalid characters: `< > : " / \ | ? *`
- Replaces multiple spaces with single space
- Trims leading/trailing whitespace
- Limits length to 100 characters (adds "..." if truncated)

## Example Folder Path

**Original Title**: `"Top 5 best gaming headphones 2025 | Must-Have Tech!"`

**Sanitized Folder**: `"Top 5 best gaming headphones 2025 Must-Have Tech"`

**Full Path**: `ReviewCh3kr_Media/Top 5 best gaming headphones 2025 Must-Have Tech/Images/rec2EaBLz3a7ukB0Z/product1.jpg`

## Benefits

1. **Better Organization**: Each project has its own folder
2. **Easier Navigation**: Find all media for a project in one place
3. **Cleaner Structure**: No mixed content from different projects
4. **Human-Friendly**: Folder names are recognizable titles instead of record IDs

## Next Steps

1. Complete remaining subagent updates (voice, video)
2. Update parent agents to pass project_title
3. Update orchestrator to extract and distribute project_title
4. Test with sample upload
5. Update main documentation
6. Commit and push all changes

## Code Changes Summary

**Files Modified**: 5
- `src/mcp/production_enhanced_google_drive_agent_mcp.py` (+40 lines)
- `src/utils/dual_storage_manager.py` (+5 lines)
- `agents/content_generation/image_generator_subagent.py` (+4 lines)
- `agents/content_generation/voice_generator_subagent.py` (+2 lines)

**Files Remaining**: 4
- `agents/content_generation/voice_generator_subagent.py` (complete execute_task)
- `agents/video_production/wow_video_subagent.py`
- `agents/content_generation/agent.py`
- `agents/orchestrator.py`

**Total Implementation Time**: ~45 minutes (50% complete)
