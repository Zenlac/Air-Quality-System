#!/usr/bin/env python3
"""
Guide Update Script for Air Pollution Forecasting System

This script provides easy commands to keep the USER_GUIDE.md updated
automatically when system changes occur.

Usage:
    python update_guide.py --check          # Check for updates
    python update_guide.py --force          # Force update
    python update_guide.py --setup          # Setup auto-update
    python update_guide.py --watch          # Watch for changes (continuous)
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.guide_updater import GuideUpdater
from src.utils import setup_logging


def check_for_updates(updater: GuideUpdater, force: bool = False) -> bool:
    """
    Check for and apply updates to the guide
    
    Args:
        updater: GuideUpdater instance
        force: Force update even if no changes
        
    Returns:
        True if updated, False otherwise
    """
    print("Checking for system changes...")
    
    changed_files = updater.detect_changes()
    
    if not changed_files and not force:
        print("No changes detected - USER_GUIDE.md is up to date")
        return False
    
    if force:
        print("Force update requested")
        changed_files = ["Force update requested"]
    
    print(f"Changes detected in {len(changed_files)} files:")
    for file_path in changed_files[:5]:  # Show first 5
        print(f"   • {file_path}")
    if len(changed_files) > 5:
        print(f"   ... and {len(changed_files) - 5} more")
    
    # Update the guide
    updated = updater.check_and_update(force_update=force)
    
    if updated:
        print("USER_GUIDE.md has been successfully updated!")
        print(f"Timestamp: {updater.extract_system_info()['timestamp']}")
    else:
        print("Failed to update USER_GUIDE.md")
    
    return updated


def setup_auto_update(updater: GuideUpdater):
    """
    Setup the automatic update system
    
    Args:
        updater: GuideUpdater instance
    """
    print("Setting up automatic guide updates...")
    
    updater.setup_auto_update()
    
    print("Auto-update system is ready!")
    print("Hash file created: .guide_hashes.json")
    print("Run 'python update_guide.py --check' to verify setup")


def watch_for_changes(updater: GuideUpdater, interval: int = 30):
    """
    Continuously watch for changes and update the guide
    
    Args:
        updater: GuideUpdater instance
        interval: Check interval in seconds
    """
    print(f"Watching for changes (checking every {interval} seconds)...")
    print("Press Ctrl+C to stop watching")
    
    try:
        while True:
            updated = check_for_updates(updater)
            
            if updated:
                print("Guide updated - continuing to watch...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nStopped watching for changes")


def show_status(updater: GuideUpdater):
    """
    Show current status of the guide updater
    
    Args:
        updater: GuideUpdater instance
    """
    print("Guide Updater Status")
    print("=" * 40)
    
    # System info
    system_info = updater.extract_system_info()
    print(f"Last Check: {system_info['timestamp']}")
    print(f"Version: {system_info['version']}")
    
    # Monitored files
    current_hashes = updater.get_current_hashes()
    print(f"Monitored Files: {len(current_hashes)}")
    
    # Saved hashes
    saved_hashes = updater.load_saved_hashes()
    if saved_hashes:
        print(f"Saved Hashes: {len(saved_hashes)}")
        print(f"Last Update: {datetime.fromtimestamp(updater.hash_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("No saved hashes found - run --setup first")
    
    # Recent changes
    changed_files = updater.detect_changes()
    if changed_files:
        print(f"Pending Changes: {len(changed_files)}")
    else:
        print("No pending changes")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Keep USER_GUIDE.md updated automatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python update_guide.py --check          # Check for updates
    python update_guide.py --force          # Force update guide
    python update_guide.py --setup          # Setup auto-update system
    python update_guide.py --watch          # Watch for changes continuously
    python update_guide.py --status         # Show current status
        """
    )
    
    parser.add_argument("--check", action="store_true", 
                       help="Check for updates and apply if needed")
    parser.add_argument("--force", action="store_true", 
                       help="Force update even if no changes detected")
    parser.add_argument("--setup", action="store_true", 
                       help="Setup automatic update system")
    parser.add_argument("--watch", action="store_true", 
                       help="Continuously watch for changes")
    parser.add_argument("--status", action="store_true", 
                       help="Show current status")
    parser.add_argument("--interval", type=int, default=30,
                       help="Watch interval in seconds (default: 30)")
    parser.add_argument("--verbose", action="store_true", 
                       help="Enable verbose logging")
    parser.add_argument("--project-root", type=str,
                       help="Project root directory (default: current directory)")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Determine project root
    project_root = args.project_root or os.path.dirname(os.path.abspath(__file__))
    
    # Initialize updater
    updater = GuideUpdater(project_root)
    
    # Execute command
    if args.setup:
        setup_auto_update(updater)
    elif args.watch:
        watch_for_changes(updater, args.interval)
    elif args.status:
        show_status(updater)
    elif args.check or args.force:
        check_for_updates(updater, force=args.force)
    else:
        # Default behavior - check for updates
        check_for_updates(updater)


if __name__ == "__main__":
    main()
