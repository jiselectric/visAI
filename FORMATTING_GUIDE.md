# Python Auto Formatting Guide

## 🎨 Auto Formatting Setup Complete!

Your project now has automatic code formatting configured with:

- **Black** - Code formatter (88 character line length)
- **isort** - Import sorter (compatible with Black)
- **pre-commit** - Automatic formatting on git commits
- **VS Code integration** - Format on save

## 🚀 How to Use

### Automatic Formatting (Recommended)
1. **VS Code**: Just save any Python file (`Cmd+S`) - it will auto-format
2. **Git Commits**: Pre-commit hooks will format code automatically before commits

### Manual Formatting
```bash
# Format all Python files
python format_code.py

# Or use individual tools
black .
isort .
```

### Check Formatting
```bash
# Check if files are properly formatted
black --check .
isort --check-only .
```

## ⚙️ Configuration Files

- **`pyproject.toml`** - Black and isort configuration
- **`.pre-commit-config.yaml`** - Pre-commit hooks configuration
- **`.vscode/settings.json`** - VS Code formatting settings

## 🎯 Features

✅ **88 character line length** (Black standard)  
✅ **Import sorting** (isort with Black profile)  
✅ **Format on save** (VS Code)  
✅ **Pre-commit hooks** (automatic before git commits)  
✅ **Consistent code style** across the project  

## 🔧 VS Code Extensions

Make sure you have these extensions installed:
- Python (Microsoft)
- Black Formatter
- isort

## 📝 Notes

- All formatting config files are in `.gitignore` to avoid committing personal settings
- The `format_code.py` script is also in `.gitignore` as it's a development tool
- Pre-commit hooks are installed and will run automatically on commits 