#!/usr/bin/env python3
# __main__.py
"""Entry point for L3P - Low-Profile Performance Profile."""

import argparse
import sys


def main() -> int:
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        prog='l3p',
        description='L3P - Low-Profile Performance Profile: A lightweight cross-platform system monitor'
    )
    
    parser.add_argument(
        '--tray-only',
        action='store_true',
        help='Run only the tray icon without profile window support'
    )
    
    parser.add_argument(
        '--profile-only',
        action='store_true',
        help='Run only the profile window without tray icon'
    )
    
    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information and exit'
    )

    args = parser.parse_args()

    # Handle version flag
    if args.version:
        from .version import VERSION, BUILD_DATE
        print(f"L3P v{VERSION} (built {BUILD_DATE})")
        return 0

    # Import app modules after argument parsing for faster --help/--version
    from .app import L3PApp, run_tray_only, run_profile_only

    try:
        if args.tray_only:
            run_tray_only()
        elif args.profile_only:
            run_profile_only()
        else:
            app = L3PApp()
            app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
