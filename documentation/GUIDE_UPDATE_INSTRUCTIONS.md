# Guide Update System Instructions

*Last Updated: February 27, 2026*

This document explains how to use the automatic USER_GUIDE.md update system that keeps your documentation synchronized with system changes.

## 🎯 Overview

The Guide Update System automatically:
- Detects changes in source code, configuration, and example files
- Updates the USER_GUIDE.md timestamp and version information
- Adds changelog entries for tracked changes
- Maintains documentation consistency

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Setup the automatic update system
python update_guide.py --setup
```

This creates:
- `.guide_hashes.json` - File tracking system state
- Initial baseline of current file hashes

### 2. Check for Updates

```bash
# Check and apply any pending updates
python update_guide.py --check
```

### 3. Force Update

```bash
# Force update even if no changes detected
python update_guide.py --force
```

## 📋 Available Commands

### update_guide.py Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `--setup` | Initialize the update system | First time setup |
| `--check` | Check for and apply updates | Regular maintenance |
| `--force` | Force update guide | Manual refresh |
| `--status` | Show current system status | Diagnostics |
| `--watch` | Continuously monitor changes | Development mode |

### main.py Integration

| Command | Description | Use Case |
|---------|-------------|----------|
| `--update-guide` | Check guide updates before execution | Before running forecasts |
| `--setup-guide` | Setup guide update system | One-time initialization |

## 🔧 How It Works

### File Monitoring

The system monitors these files and directories:

- **src/** - All Python source files
- **config.yaml** - Configuration parameters
- **example_usage.py** - Example functions
- **README.md** - Project documentation
- **requirements.txt** - Dependencies

### Change Detection

1. **Hash Calculation**: Each monitored file gets a SHA256 hash
2. **Comparison**: Current hashes compared to saved baseline
3. **Change Detection**: Any hash difference triggers an update
4. **Documentation Update**: USER_GUIDE.md gets updated with changes

### Update Process

1. **Header Update**: Timestamp and version information refreshed
2. **Changelog Entry**: New section added with change details
3. **Hash Save**: New baseline saved for future comparisons

## 📊 Status Monitoring

### Check System Status

```bash
python update_guide.py --status
```

Output shows:
- Last check timestamp
- System version
- Number of monitored files
- Saved hash status
- Pending changes

### Example Status Output

```
Guide Updater Status
========================================
Last Check: 2026-02-27 08:55:28
Version: 1.0.0
Monitored Files: 15
Saved Hashes: 15
Last Update: 2026-02-27 08:55:28
No pending changes
```

## 🔄 Continuous Monitoring

### Development Mode

```bash
# Watch for changes continuously (checks every 30 seconds)
python update_guide.py --watch

# Custom interval (every 60 seconds)
python update_guide.py --watch --interval 60
```

Use this during development to automatically update documentation as you make changes.

Press `Ctrl+C` to stop watching.

## 📝 Changelog Format

When changes are detected, the system adds entries like:

```markdown
## 🔄 Changes - 2026-02-27 08:55:28

### Source Code
- Updated `src/guide_updater.py`

### Configuration
- Updated configuration parameters

### Documentation
- Updated `README.md`
```

## ⚙️ Configuration

### Monitored File Patterns

You can customize monitored files by editing `src/guide_updater.py`:

```python
self.monitored_paths = {
    "src": ["*.py"],
    "config.yaml": ["config.yaml"],
    "example_usage.py": ["example_usage.py"],
    "README.md": ["README.md"],
    "requirements.txt": ["requirements.txt"]
}
```

### Update Frequency

- **Manual**: Use `--check` when needed
- **Integrated**: Use `--update-guide` with main.py
- **Continuous**: Use `--watch` during development

## 🚨 Troubleshooting

### Common Issues

#### 1. "No saved hashes found"
**Solution**: Run `python update_guide.py --setup` first

#### 2. Encoding errors
**Solution**: The system now uses UTF-8 encoding for all file operations

#### 3. Permission denied
**Solution**: Ensure write permissions to project directory

#### 4. File not found errors
**Solution**: Verify you're in the correct project directory

### Debug Mode

```bash
# Enable verbose logging
python update_guide.py --check --verbose

# Or with main.py
python main.py --update-guide --verbose
```

## 🎯 Best Practices

### Development Workflow

1. **Start Development**: Run `python update_guide.py --watch`
2. **Make Changes**: Edit source files as needed
3. **Check Updates**: Guide updates automatically
4. **Verify Documentation**: Review USER_GUIDE.md changes
5. **Commit Changes**: Include updated documentation

### Before Releases

```bash
# Ensure documentation is current
python update_guide.py --force

# Check status
python update_guide.py --status

# Review changelog entries in USER_GUIDE.md
```

### Regular Maintenance

- Run `--check` weekly to ensure documentation sync
- Review changelog entries for accuracy
- Clean up old changelog entries if needed

## 🔗 Integration Examples

### Git Hooks

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python update_guide.py --force
git add USER_GUIDE.md
```

### CI/CD Pipeline

Add to your pipeline:

```yaml
- name: Update Documentation
  run: python update_guide.py --force
- name: Commit Updated Docs
  run: |
    git config --local user.email "action@github.com"
    git config --local user.name "GitHub Action"
    git add USER_GUIDE.md
    git commit -m "Auto-update documentation" || exit 0
```

### Makefile Integration

```makefile
update-docs:
	python update_guide.py --force

check-docs:
	python update_guide.py --check

.PHONY: update-docs check-docs
```

## 📚 File Structure

```
Air Pollution System/
├── USER_GUIDE.md              # Main documentation (auto-updated)
├── update_guide.py            # Update script
├── src/
│   └── guide_updater.py      # Core update logic
├── .guide_hashes.json        # System state tracking
└── GUIDE_UPDATE_INSTRUCTIONS.md # This file
```

## 🆘 Getting Help

### Command Line Help

```bash
python update_guide.py --help
python main.py --help
```

### Log Files

Check the system log for detailed information:
- `air_pollution_system.log` - Main system logs
- Console output with `--verbose` flag

### Support

If you encounter issues:
1. Check this documentation first
2. Run with `--verbose` for detailed logs
3. Verify file permissions and paths
4. Check the troubleshooting section above

---

**Air Quality Commission**  
*Keeping documentation synchronized with system evolution*
