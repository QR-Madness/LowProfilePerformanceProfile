# version.py
"""Version information for L3P."""

import sys


def is_frozen() -> bool:
    """Check if the application is running from a frozen executable."""
    return getattr(sys, 'frozen', False)


def get_version() -> str:
    """Get the version string with the 'dev' prefix for unfrozen environments."""
    base_version = '2.0.0'
    return base_version if is_frozen() else f'dev-{base_version}'


VERSION = get_version()
BUILD_DATE = '2026-01-12'
