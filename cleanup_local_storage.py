#!/usr/bin/env python3
"""
Local Storage Cleanup Script
============================
Cleans up old media files to prevent disk space issues.
Can be run manually or via cron job.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import logging
import argparse
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LocalStorageCleanup:
    """Manages cleanup of local media storage"""
    
    def __init__(self, base_path: str = "/home/claude-workflow/media_storage", 
                 days_to_keep: int = 7,
                 dry_run: bool = False):
        self.base_path = Path(base_path)
        self.days_to_keep = days_to_keep
        self.dry_run = dry_run
        
        # Also clean temp directories
        self.temp_paths = [
            Path("/tmp/remotion-renders"),
            Path("/tmp/workflow-temp")
        ]
        
        self.stats = {
            'directories_removed': 0,
            'files_removed': 0,
            'space_freed_mb': 0,
            'errors': []
        }
    
    def cleanup(self):
        """Main cleanup process"""
        logger.info(f"""
╔══════════════════════════════════════════════╗
║   LOCAL STORAGE CLEANUP                      ║
╠══════════════════════════════════════════════╣
║   Base Path: {str(self.base_path):<32} ║
║   Keep Days: {self.days_to_keep:<32} ║
║   Dry Run: {str(self.dry_run):<34} ║
╚══════════════════════════════════════════════╝
""")
        
        # Clean main storage
        self._clean_directory(self.base_path)
        
        # Clean temp directories
        for temp_path in self.temp_paths:
            if temp_path.exists():
                self._clean_directory(temp_path, is_temp=True)
        
        # Print summary
        self._print_summary()
    
    def _clean_directory(self, base_path: Path, is_temp: bool = False):
        """Clean a specific directory"""
        if not base_path.exists():
            logger.warning(f"Path does not exist: {base_path}")
            return
        
        cutoff_date = datetime.now() - timedelta(days=self.days_to_keep)
        
        # For temp directories, use shorter retention (1 day)
        if is_temp:
            cutoff_date = datetime.now() - timedelta(days=1)
        
        logger.info(f"Scanning {base_path}...")
        
        # Look for date-based directories (YYYY-MM-DD format)
        for item in base_path.iterdir():
            try:
                if item.is_dir():
                    # Check if it's a date directory
                    if self._is_date_directory(item.name):
                        dir_date = self._parse_date_directory(item.name)
                        if dir_date and dir_date < cutoff_date:
                            self._remove_directory(item)
                    # For temp dirs, check modification time
                    elif is_temp:
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime < cutoff_date:
                            self._remove_directory(item)
                
                # Clean old files in root (not in date directories)
                elif item.is_file() and not self._is_date_directory(item.parent.name):
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff_date:
                        self._remove_file(item)
                        
            except Exception as e:
                logger.error(f"Error processing {item}: {e}")
                self.stats['errors'].append(str(e))
    
    def _is_date_directory(self, name: str) -> bool:
        """Check if directory name is in YYYY-MM-DD format"""
        try:
            datetime.strptime(name, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def _parse_date_directory(self, name: str) -> Optional[datetime]:
        """Parse date from directory name"""
        try:
            return datetime.strptime(name, "%Y-%m-%d")
        except ValueError:
            return None
    
    def _remove_directory(self, path: Path):
        """Remove a directory and all contents"""
        try:
            # Calculate size before removal
            size_mb = self._get_directory_size(path) / (1024 * 1024)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove directory: {path} ({size_mb:.2f} MB)")
            else:
                shutil.rmtree(path)
                logger.info(f"✅ Removed directory: {path} ({size_mb:.2f} MB)")
            
            self.stats['directories_removed'] += 1
            self.stats['space_freed_mb'] += size_mb
            
        except Exception as e:
            logger.error(f"Failed to remove directory {path}: {e}")
            self.stats['errors'].append(str(e))
    
    def _remove_file(self, path: Path):
        """Remove a single file"""
        try:
            size_mb = path.stat().st_size / (1024 * 1024)
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Would remove file: {path} ({size_mb:.2f} MB)")
            else:
                path.unlink()
                logger.info(f"✅ Removed file: {path} ({size_mb:.2f} MB)")
            
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
        logger.info(f"""
╔══════════════════════════════════════════════╗
║   CLEANUP SUMMARY                            ║
╠══════════════════════════════════════════════╣
║   Directories Removed: {self.stats['directories_removed']:<22} ║
║   Files Removed: {self.stats['files_removed']:<28} ║
║   Space Freed: {self.stats['space_freed_mb']:.2f} MB{' ' * (25 - len(f"{self.stats['space_freed_mb']:.2f} MB"))} ║
║   Errors: {len(self.stats['errors']):<35} ║
╚══════════════════════════════════════════════╝
""")
        
        if self.dry_run:
            logger.info("ℹ️ This was a DRY RUN - no files were actually deleted")
        
        # Save stats to file
        stats_file = Path("/home/claude-workflow/cleanup_stats.json")
        self.stats['timestamp'] = datetime.now().isoformat()
        self.stats['dry_run'] = self.dry_run
        
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
        
        logger.info(f"📊 Stats saved to {stats_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Clean up old local media files')
    parser.add_argument('--days', type=int, default=7, 
                       help='Number of days to keep files (default: 7)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--path', type=str, default='/home/claude-workflow/media_storage',
                       help='Base path for media storage')
    
    args = parser.parse_args()
    
    # Run cleanup
    cleaner = LocalStorageCleanup(
        base_path=args.path,
        days_to_keep=args.days,
        dry_run=args.dry_run
    )
    
    cleaner.cleanup()


if __name__ == "__main__":
    main()