# version.py
import sys


def is_frozen():
    """Check if the application is running from a frozen executable"""
    return getattr(sys, 'frozen', False)


def get_version():
    """Get the version string with 'dev' prefix for unfrozen environments"""
    base_version = '1.0.0'
    return base_version if is_frozen() else f'dev-{base_version}'


VERSION = get_version()
BUILD_DATE = '2025-06-05'
