# L3P - Low-Profile Performance Profile

A lightweight, cross-platform system monitoring tool that displays CPU, Memory, and Disk usage in your system tray.

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- 🖥️ **Cross-platform** - Works on Windows and Linux
- 📊 **Real-time monitoring** - CPU, Memory, and Disk usage at a glance
- 🎨 **Visual tray icon** - Color-coded bars show resource usage
- 📋 **Detailed profile window** - In-depth system metrics with DearPyGui
- 🪶 **Lightweight** - Minimal resource footprint
- 🎯 **Easy to use** - Just run and check your system tray

## Screenshots

The tray icon shows three bars:
- 🟢 **Green** - CPU usage
- 🔴 **Red** - Memory usage  
- 🔵 **Blue** - Disk usage

Hover over the icon for exact values. Right-click for menu options.

## Installation

### From Source (using UV)

This project uses [UV](https://github.com/astral-sh/uv) for fast dependency management.

```bash
# Clone the repository
git clone https://github.com/example/l3p.git
cd l3p

# Install dependencies with UV
uv sync

# Run
uv run python -m src
```

### From Source (using pip)

```bash
# Clone the repository
git clone https://github.com/example/l3p.git
cd l3p

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run
python -m src
```

### Linux-Specific Setup

The app auto-detects your desktop environment and uses the best backend:

- **KDE Plasma**: Uses PyQt6 (included by default) - works out of the box!
- **GNOME/Unity**: Needs PyGObject for AppIndicator support
- **Other (XFCE, MATE, etc.)**: Usually works with pystray's default backend

**For GNOME users (optional):**
```bash
sudo apt install gir1.2-appindicator3-0.1 libgirepository1.0-dev
pip install pygobject
```

## Usage

### Run with Tray + Profile Window

```bash
python -m src
```

This starts the tray icon. Right-click and select "Show Profile" to open the detailed metrics window.

### Run Tray Only

```bash
python -m src --tray-only
```

Runs only the system tray icon without profile window support (lower memory usage).

### Run Profile Window Only

```bash
python -m src --profile-only
```

Runs only the profile window without the tray icon.

### Command Line Options

```
usage: l3p [-h] [--tray-only] [--profile-only] [--version]

L3P - Low-Profile Performance Profile

options:
  -h, --help      show this help message and exit
  --tray-only     Run only the tray icon without profile window support
  --profile-only  Run only the profile window without tray icon
  --version       Show version information and exit
```

## Building Standalone Executable

```bash
# Build for your current platform
python build.py

# The executable will be in the 'dist' folder
./dist/l3p          # Linux
.\dist\l3p.exe      # Windows
```

### Windows Quick Launch Tip

Add the built executable to your PATH or create a shortcut in your Startup folder for auto-start.

### Linux Autostart

Create `~/.config/autostart/l3p.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=L3P System Monitor
Exec=/path/to/l3p --tray-only
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
```

## System Requirements

- **Python:** 3.10 or later
- **Windows:** Windows 10 or later
- **Linux:** Most modern distributions with a system tray
  - GNOME: Requires AppIndicator extension
  - KDE Plasma: Works natively
  - XFCE/MATE/Cinnamon: Should work natively

## Project Structure

```
l3p/
├── src/
│   ├── __init__.py         # Package init
│   ├── __main__.py         # Entry point with CLI
│   ├── app.py              # Main application controller
│   ├── metrics.py          # System metrics collection
│   ├── profile_window.py   # DearPyGui detailed view
│   ├── tray.py             # System tray icon
│   └── version.py          # Version information
├── build.py                # Build script
├── pyproject.toml          # Project configuration
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Development

```bash
# Install in development mode (using UV)
uv sync --dev

# Or using pip
pip install -e ".[dev]"

# Run tests
uv run pytest

# Build executable
uv run python build.py
```

## Troubleshooting

### Tray Icon Not Showing (Linux)

1. **GNOME:** Install the [AppIndicator extension](https://extensions.gnome.org/extension/615/appindicator-support/)
2. Install the AppIndicator library for your distro (see Linux-Specific Setup)
3. Try running with `PYSTRAY_BACKEND=gtk python -m src`

### Profile Window Not Opening

DearPyGui requires OpenGL. Make sure your graphics drivers are up to date.

### High CPU Usage

Increase the update interval in the profile window slider, or use `--tray-only` mode.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.