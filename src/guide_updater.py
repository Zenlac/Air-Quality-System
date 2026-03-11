#!/usr/bin/env python3
"""
Automatic User Guide Updater for Air Pollution Forecasting System

This module automatically updates the USER_GUIDE.md document whenever
changes are detected in the system source code, configuration, or examples.

Author: Air Quality Commission
Created: 2026-02-27
"""

import os
import sys
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.utils import setup_logging


class GuideUpdater:
    """
    Automatically updates USER_GUIDE.md based on system changes
    """
    
    def __init__(self, project_root: str = None):
        """
        Initialize the guide updater
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.guide_path = self.project_root / "USER_GUIDE.md"
        self.hash_file = self.project_root / ".guide_hashes.json"
        self.config = Config(self.project_root / "config.yaml")
        
        # Files and directories to monitor
        self.monitored_paths = {
            "src": ["*.py"],
            "config.yaml": ["config.yaml"],
            "example_usage.py": ["example_usage.py"],
            "README.md": ["README.md"],
            "requirements.txt": ["requirements.txt"]
        }
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash string
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not hash {file_path}: {e}")
            return ""
    
    def get_current_hashes(self) -> Dict[str, str]:
        """
        Calculate current hashes for all monitored files
        
        Returns:
            Dictionary mapping file paths to their hashes
        """
        current_hashes = {}
        
        for path_pattern, extensions in self.monitored_paths.items():
            path = self.project_root / path_pattern
            
            if path.is_file():
                # Single file
                current_hashes[str(path)] = self.calculate_file_hash(path)
            elif path.is_dir():
                # Directory with pattern matching
                for ext in extensions:
                    for file_path in path.glob(ext):
                        current_hashes[str(file_path)] = self.calculate_file_hash(file_path)
        
        return current_hashes
    
    def load_saved_hashes(self) -> Dict[str, str]:
        """
        Load previously saved file hashes
        
        Returns:
            Dictionary of saved hashes
        """
        if not self.hash_file.exists():
            return {}
        
        try:
            with open(self.hash_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load saved hashes: {e}")
            return {}
    
    def save_hashes(self, hashes: Dict[str, str]):
        """
        Save current file hashes
        
        Args:
            hashes: Dictionary of file hashes
        """
        try:
            with open(self.hash_file, 'w') as f:
                json.dump(hashes, f, indent=2)
        except Exception as e:
            self.logger.error(f"Could not save hashes: {e}")
    
    def detect_changes(self) -> List[str]:
        """
        Detect which files have changed since last check
        
        Returns:
            List of changed file paths
        """
        current_hashes = self.get_current_hashes()
        saved_hashes = self.load_saved_hashes()
        
        changed_files = []
        
        for file_path, current_hash in current_hashes.items():
            saved_hash = saved_hashes.get(file_path, "")
            if current_hash != saved_hash:
                changed_files.append(file_path)
        
        # Check for deleted files
        for file_path in saved_hashes:
            if file_path not in current_hashes:
                changed_files.append(f"DELETED: {file_path}")
        
        return changed_files
    
    def extract_system_info(self) -> Dict:
        """
        Extract current system information for documentation
        
        Returns:
            Dictionary containing system information
        """
        info = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": self._get_version_info(),
            "config": self._get_config_summary(),
            "features": self._extract_features(),
            "dependencies": self._get_dependencies(),
            "examples": self._get_example_functions()
        }
        return info
    
    def _get_version_info(self) -> str:
        """Extract version information"""
        # Try to get version from various sources
        version_sources = [
            "setup.py",
            "pyproject.toml", 
            "__init__.py"
        ]
        
        for source in version_sources:
            file_path = self.project_root / source
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    if "version" in content.lower():
                        # Simple version extraction
                        import re
                        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                        if version_match:
                            return version_match.group(1)
                except:
                    pass
        
        return "1.0.0"  # Default version
    
    def _get_config_summary(self) -> Dict:
        """Extract configuration summary"""
        try:
            config_dict = self.config.config
            summary = {
                "data_columns": config_dict.get("data", {}).get("pollutant_columns", []),
                "forecast_horizon": config_dict.get("forecasting", {}).get("default_horizon", 14),
                "model_weights": {
                    "prophet": config_dict.get("forecasting", {}).get("prophet_weight", 0.7),
                    "arima": config_dict.get("forecasting", {}).get("arima_weight", 0.3)
                },
                "performance_settings": config_dict.get("performance", {})
            }
            return summary
        except Exception as e:
            self.logger.warning(f"Could not extract config summary: {e}")
            return {}
    
    def _extract_features(self) -> List[str]:
        """Extract system features from source code"""
        features = []
        
        # Scan source files for feature indicators
        src_dir = self.project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.glob("*.py"):
                try:
                    content = py_file.read_text()
                    
                    # Look for class definitions that might indicate features
                    import re
                    classes = re.findall(r'class\s+(\w+)', content)
                    for cls in classes:
                        if cls not in ["Config", "GuideUpdater"]:
                            features.append(cls)
                            
                    # Look for function definitions
                    functions = re.findall(r'def\s+(\w+)', content)
                    for func in functions:
                        if any(keyword in func.lower() for keyword in ["forecast", "predict", "train", "visualize"]):
                            features.append(func)
                            
                except Exception as e:
                    self.logger.warning(f"Could not analyze {py_file}: {e}")
        
        return list(set(features))  # Remove duplicates
    
    def _get_dependencies(self) -> List[str]:
        """Extract dependencies from requirements.txt"""
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                content = req_file.read_text()
                deps = [line.strip().split('==')[0].split('>=')[0] 
                       for line in content.split('\n') 
                       if line.strip() and not line.startswith('#')]
                return deps
            except Exception as e:
                self.logger.warning(f"Could not read requirements: {e}")
        
        return []
    
    def _get_example_functions(self) -> List[str]:
        """Extract example functions from example_usage.py"""
        example_file = self.project_root / "example_usage.py"
        if example_file.exists():
            try:
                content = example_file.read_text()
                import re
                functions = re.findall(r'def\s+(example_\w+)', content)
                return functions
            except Exception as e:
                self.logger.warning(f"Could not extract examples: {e}")
        
        return []
    
    def update_guide_header(self, system_info: Dict):
        """
        Update the header section of USER_GUIDE.md with current system info
        
        Args:
            system_info: Dictionary containing system information
        """
        if not self.guide_path.exists():
            self.logger.warning("USER_GUIDE.md not found - cannot update")
            return
        
        try:
            # Read current guide with UTF-8 encoding
            with open(self.guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update timestamp
            timestamp_line = f"*Last Updated: {system_info['timestamp']}*"
            
            # Replace timestamp line
            import re
            content = re.sub(r'\*Last Updated:.*\*', timestamp_line, content)
            
            # Update version if found
            if "version" in content.lower():
                version_line = f"**Version:** {system_info['version']}"
                content = re.sub(r'\*\*Version:\*\*.*', version_line, content)
            
            # Write updated content with UTF-8 encoding
            with open(self.guide_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.logger.info(f"Updated USER_GUIDE.md header with timestamp {system_info['timestamp']}")
            
        except Exception as e:
            self.logger.error(f"Failed to update guide header: {e}")
    
    def generate_changelog_entry(self, changed_files: List[str]) -> str:
        """
        Generate a changelog entry for the changed files
        
        Args:
            changed_files: List of changed file paths
            
        Returns:
            Changelog entry string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n## 🔄 Changes - {timestamp}\n\n"
        
        # Categorize changes
        categories = {
            "Source Code": [],
            "Configuration": [],
            "Documentation": [],
            "Examples": [],
            "Dependencies": [],
            "Other": []
        }
        
        for file_path in changed_files:
            if "DELETED:" in file_path:
                categories["Other"].append(f"- {file_path}")
            elif "src/" in file_path:
                categories["Source Code"].append(f"- Updated `{file_path}`")
            elif "config.yaml" in file_path:
                categories["Configuration"].append(f"- Updated configuration parameters")
            elif "README.md" in file_path or "USER_GUIDE.md" in file_path:
                categories["Documentation"].append(f"- Updated `{Path(file_path).name}`")
            elif "example_usage.py" in file_path:
                categories["Examples"].append(f"- Updated example functions")
            elif "requirements.txt" in file_path:
                categories["Dependencies"].append(f"- Updated dependencies")
            else:
                categories["Other"].append(f"- Updated `{Path(file_path).name}`")
        
        # Build entry
        for category, items in categories.items():
            if items:
                entry += f"### {category}\n"
                entry += "\n".join(items) + "\n\n"
        
        return entry
    
    def add_changelog_entry(self, changed_files: List[str]):
        """
        Add a changelog entry to the guide
        
        Args:
            changed_files: List of changed files
        """
        if not changed_files:
            return
        
        try:
            # Read current guide with UTF-8 encoding
            with open(self.guide_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate changelog entry
            changelog_entry = self.generate_changelog_entry(changed_files)
            
            # Find where to insert the changelog (before the final section)
            # Look for the "---" separator at the end
            separator_index = content.rfind("---")
            if separator_index != -1:
                # Insert before the separator
                new_content = content[:separator_index] + changelog_entry + "\n---\n\n" + content[separator_index:]
            else:
                # Append to end
                new_content = content + changelog_entry
            
            # Write updated content with UTF-8 encoding
            with open(self.guide_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.logger.info(f"Added changelog entry for {len(changed_files)} changed files")
            
        except Exception as e:
            self.logger.error(f"Failed to add changelog entry: {e}")
    
    def check_and_update(self, force_update: bool = False) -> bool:
        """
        Check for changes and update the guide if necessary
        
        Args:
            force_update: Force update even if no changes detected
            
        Returns:
            True if guide was updated, False otherwise
        """
        self.logger.info("Checking for system changes...")
        
        # Detect changes
        changed_files = self.detect_changes()
        
        if not changed_files and not force_update:
            self.logger.info("No changes detected - guide is up to date")
            return False
        
        if force_update:
            self.logger.info("Force update requested")
            changed_files = ["Force update requested"]
        
        self.logger.info(f"Changes detected in {len(changed_files)} files")
        
        # Get current system info
        system_info = self.extract_system_info()
        
        # Update guide header
        self.update_guide_header(system_info)
        
        # Add changelog entry
        self.add_changelog_entry(changed_files)
        
        # Save current hashes
        current_hashes = self.get_current_hashes()
        self.save_hashes(current_hashes)
        
        self.logger.info("USER_GUIDE.md updated successfully")
        return True
    
    def setup_auto_update(self):
        """
        Setup automatic update monitoring
        """
        self.logger.info("Setting up automatic guide updates...")
        
        # Create initial hash file if it doesn't exist
        if not self.hash_file.exists():
            current_hashes = self.get_current_hashes()
            self.save_hashes(current_hashes)
            self.logger.info("Created initial hash file")
        
        # Perform initial update
        self.check_and_update(force_update=True)


def main():
    """Main function for standalone execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Update USER_GUIDE.md automatically")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument("--force", action="store_true", help="Force update")
    parser.add_argument("--setup", action="store_true", help="Setup auto-update")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    
    # Initialize updater
    updater = GuideUpdater(args.project_root)
    
    if args.setup:
        updater.setup_auto_update()
    else:
        updated = updater.check_and_update(force_update=args.force)
        if updated:
            print("USER_GUIDE.md has been updated")
        else:
            print("No updates needed")


if __name__ == "__main__":
    main()
