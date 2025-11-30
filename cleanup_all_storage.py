#!/usr/bin/env python3
"""
Weekly Complete Storage Cleanup Script
=======================================
Runs every Sunday at 07:00 and deletes ALL files in media storage.
Complete cleanup - no age checking, removes everything.

Usage:
    python3 cleanup_all_storage.py           # Delete ALL files
    python3 cleanup_all_storage.py --dry-run # Preview what would be deleted
    python3 cleanup_all_storage.py --backup  # Backup to Drive before deletion
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple
import logging
import argparse
import json
import asyncio
import sys

# Add project to path
sys.path.append('/home/claude-workflow')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/claude-workflow/cleanup_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompleteStorageCleanup:
    """Manages complete cleanup of ALL files in local media storage"""
    
    def __init__(self, 
                 base_path: str = "/home/claude-workflow/media_storage",
                 dry_run: bool = False,
                 backup: bool = False):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.backup = backup
        
        # Load config for potential backup
        config_path = '/home/claude-workflow/config/api_keys.json'
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Also clean temp directories
        self.temp_paths = [
            Path("/tmp/remotion-renders"),
            Path("/tmp/workflow-temp"),
            Path("/home/claude-workflow/temp")
        ]
        
        self.stats = {
            'directories_removed': 0,
            'files_removed': 0,
            'space_freed_mb': 0,
            'files_backed_up': 0,
            'backup_size_mb': 0,
            'errors': []
        }
    
    async def cleanup_all(self):
        """Main cleanup process - removes ALL files"""
        logger.info(f"""
╔══════════════════════════════════════════════╗
║   WEEKLY COMPLETE STORAGE CLEANUP            ║
╠══════════════════════════════════════════════╣
║   Schedule: Every Sunday at 07:00            ║
║   Action: DELETE ALL FILES                   ║
║   Base Path: {str(self.base_path):<32} ║
║   Dry Run: {str(self.dry_run):<34} ║
║   Backup to Drive: {str(self.backup):<26} ║
╚══════════════════════════════════════════════╝
""")
        
        logger.warning("⚠️  WARNING: This will delete ALL files in media storage!")
        
        # Collect all items to remove
        items_to_remove = []
        
        # Scan main storage - get EVERYTHING
        if self.base_path.exists():
            items_to_remove.extend(self._scan_all_items(self.base_path))
        
        # Scan temp directories - get EVERYTHING
        for temp_path in self.temp_paths:
            if temp_path.exists():
                items_to_remove.extend(self._scan_all_items(temp_path))
        
        if not items_to_remove:
            logger.info("✅ No files found. Storage is already clean!")
            return
        
        # Calculate total size
        total_size_mb = sum(size for _, size in items_to_remove)
        total_count = len(items_to_remove)
        
        logger.info(f"""
📊 Found {total_count} items to delete:
   • Total size: {total_size_mb:.2f} MB
   • Action: DELETE ALL (no age checking)
""")
        
        # Optional backup before deletion
        if self.backup and not self.dry_run:
            await self._backup_items(items_to_remove)
        
        # Remove ALL items
        for item_path, size_mb in items_to_remove:
            if item_path.is_dir():
                self._remove_directory(item_path, size_mb)
            else:
                self._remove_file(item_path, size_mb)
        
        # Print summary
        self._print_summary()
    
    def _scan_all_items(self, base_path: Path) -> List[Tuple[Path, float]]:
        """Scan for ALL items in directory (no age checking)"""
        items = []
        
        logger.info(f"🔍 Scanning ALL items in {base_path}...")
        
        try:
            # Get everything in the base path
            for item in base_path.iterdir():
                try:
                    if item.is_dir():
                        # Calculate directory size
                        size_mb = self._get_directory_size(item) / (1024 * 1024)
                        items.append((item, size_mb))
                    elif item.is_file():
                        # Get file size
                        size_mb = item.stat().st_size / (1024 * 1024)
                        items.append((item, size_mb))
                        
                except Exception as e:
                    logger.error(f"Error scanning {item}: {e}")
                    self.stats['errors'].append(str(e))
        
        except Exception as e:
            logger.error(f"Error scanning directory {base_path}: {e}")
            self.stats['errors'].append(str(e))
        
        return items
    
    async def _backup_items(self, items):
        """Backup items to Google Drive before deletion"""
        logger.info("☁️ Backing up files to Google Drive before complete deletion...")
        
        try:
            from src.utils.dual_storage_manager import get_storage_manager
            storage_manager = get_storage_manager(self.config)
            
            backup_date = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for item_path, size_mb in items:
                if item_path.is_file() and size_mb < 100:  # Only backup files < 100MB
                    try:
                        with open(item_path, 'rb') as f:
                            content = f.read()
                        
                        # Upload to Drive with dated backup folder
                        result = await storage_manager.save_media(
                            content=content,
                            filename=item_path.name,
                            media_type="backup",
                            record_id=f"weekly_cleanup_{backup_date}",
                            upload_to_drive=True
                        )
                        
                        if result.get('drive_url'):
                            self.stats['files_backed_up'] += 1
                            self.stats['backup_size_mb'] += size_mb
                            logger.info(f"☁️ Backed up: {item_path.name} ({size_mb:.2f} MB)")
                    except Exception as e:
                        logger.warning(f"Failed to backup {item_path}: {e}")
            
            if self.stats['files_backed_up'] > 0:
                logger.info(f"✅ Backed up {self.stats['files_backed_up']} files ({self.stats['backup_size_mb']:.2f} MB)")
                
        except Exception as e:
            logger.error(f"Backup initialization failed: {e}")
            self.stats['errors'].append(f"Backup failed: {str(e)}")
    
    def _remove_directory(self, path: Path, size_mb: float):
        """Remove a directory and all contents"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove directory: {path} ({size_mb:.2f} MB)")
            else:
                shutil.rmtree(path)
                logger.info(f"🗑️ Removed directory: {path} ({size_mb:.2f} MB)")
            
            self.stats['directories_removed'] += 1
            self.stats['space_freed_mb'] += size_mb
            
        except Exception as e:
            logger.error(f"Failed to remove directory {path}: {e}")
            self.stats['errors'].append(str(e))
    
    def _remove_file(self, path: Path, size_mb: float):
        """Remove a single file"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove file: {path.name} ({size_mb:.2f} MB)")
            else:
                path.unlink()
                logger.info(f"🗑️ Removed file: {path.name} ({size_mb:.2f} MB)")
            
            self.stats['files_removed'] += 1
            self.stats['space_freed_mb'] += size_mb
            
        except Exception as e:
            logger.error(f"Failed to remove file {path}: {e}")
            self.stats['errors'].append(str(e))
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate total size of directory in bytes"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception:
            pass
        return total
    
    def _print_summary(self):
        """Print cleanup summary"""
        
        # Calculate current storage usage (should be 0 after cleanup)
        current_size = 0
        current_files = 0
        if self.base_path.exists():
            for item in self.base_path.rglob('*'):
                if item.is_file():
                    current_size += item.stat().st_size
                    current_files += 1
        current_size_mb = current_size / (1024 * 1024)
        
        logger.info(f"""
╔══════════════════════════════════════════════╗
║   COMPLETE CLEANUP SUMMARY                   ║
╠══════════════════════════════════════════════╣
║   Directories Removed: {self.stats['directories_removed']:<22} ║
║   Files Removed: {self.stats['files_removed']:<28} ║
║   Space Freed: {self.stats['space_freed_mb']:.2f} MB{' ' * (25 - len(f"{self.stats['space_freed_mb']:.2f} MB"))} ║
║   Files Backed Up: {self.stats['files_backed_up']:<25} ║
║   Backup Size: {self.stats['backup_size_mb']:.2f} MB{' ' * (25 - len(f"{self.stats['backup_size_mb']:.2f} MB"))} ║
║   Errors: {len(self.stats['errors']):<35} ║
╠══════════════════════════════════════════════╣
║   CURRENT STORAGE STATUS                     ║
║   Total Files: {current_files:<30} ║
║   Total Size: {current_size_mb:.2f} MB{' ' * (26 - len(f"{current_size_mb:.2f} MB"))} ║
╚══════════════════════════════════════════════╝
""")
        
        if self.dry_run:
            logger.info("ℹ️ This was a DRY RUN - no files were actually deleted")
        else:
            logger.info("✅ Complete cleanup executed - ALL files removed")
        
        # Save detailed report
        report_dir = Path("/home/claude-workflow/cleanup_reports")
        report_dir.mkdir(exist_ok=True)
        
        report_file = report_dir / f"complete_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.stats['timestamp'] = datetime.now().isoformat()
        self.stats['dry_run'] = self.dry_run
        self.stats['cleanup_type'] = 'COMPLETE'
        self.stats['current_files'] = current_files
        self.stats['current_size_mb'] = current_size_mb
        
        with open(report_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"📊 Report saved to {report_file}")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Complete cleanup of ALL media storage files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be deleted without actually deleting')
    parser.add_argument('--backup', action='store_true',
                       help='Backup files to Google Drive before deletion')
    parser.add_argument('--path', type=str, default='/home/claude-workflow/media_storage',
                       help='Base path for media storage')
    
    args = parser.parse_args()
    
    # Run complete cleanup
    cleaner = CompleteStorageCleanup(
        base_path=args.path,
        dry_run=args.dry_run,
        backup=args.backup
    )
    
    await cleaner.cleanup_all()


if __name__ == "__main__":
    asyncio.run(main())