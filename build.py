#!/usr/bin/env python3
"""Build script for L3P cross-platform executable."""

import os
import sys
import subprocess
import shutil
import glob
import platform


def clean_build():
    """Clean up build directories."""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name} directory...")
            shutil.rmtree(dir_name)

    for file_pattern in files_to_clean:
        for file in glob.glob(file_pattern):
            print(f"Removing {file}...")
            os.remove(file)


def build_executable():
    """Build the executable for the current platform."""
    os_type = platform.system()
    
    try:
        # Install required packages
        print("Installing dependencies...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            check=True
        )
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
            check=True
        )

        # Platform-specific separator for --add-data
        sep = ';' if os_type == 'Windows' else ':'
        
        # Build command
        build_cmd = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--name=l3p',
            '--onefile',
            '--noconsole',
            f'--add-data=README.md{sep}.',
            '--paths=.',  # Add current directory to Python path
            '--hidden-import=PIL._tkinter_finder',
            '--hidden-import=pystray._base',
            '--hidden-import=src.version',
            '--hidden-import=src.metrics',
            '--hidden-import=src.tray',
            '--hidden-import=src.tray_qt',
            '--hidden-import=src.profile_window',
            '--hidden-import=src.app',
        ]

        # Platform-specific hidden imports
        if os_type == 'Windows':
            build_cmd.extend([
                '--hidden-import=pystray._win32',
            ])
        elif os_type == 'Linux':
            build_cmd.extend([
                '--hidden-import=pystray._appindicator',
                '--hidden-import=pystray._gtk',
                '--hidden-import=pystray._xorg',
            ])
        elif os_type == 'Darwin':
            build_cmd.extend([
                '--hidden-import=pystray._darwin',
            ])

        # Add icon if it exists
        icon_file = 'app_icon.ico' if os_type == 'Windows' else 'app_icon.png'
        if os.path.exists(icon_file):
            build_cmd.append(f'--icon={icon_file}')

        # Entry point
        build_cmd.append('src/__main__.py')

        print(f"\nBuilding for {os_type}...")
        print(f"Command: {' '.join(build_cmd)}\n")

        # Execute build
        subprocess.run(build_cmd, check=True)

        print("\n" + "=" * 50)
        print("Build completed successfully!")
        print("=" * 50)
        
        # Show output location
        if os_type == 'Windows':
            exe_path = os.path.join('dist', 'l3p.exe')
        else:
            exe_path = os.path.join('dist', 'l3p')
        
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\nExecutable: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
        
        print("\nTo run:")
        print(f"  {exe_path}")
        print(f"  {exe_path} --tray-only     # Run only tray icon")
        print(f"  {exe_path} --profile-only  # Run only profile window")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build L3P executable')
    parser.add_argument('--clean', action='store_true', help='Clean build directories only')
    parser.add_argument('--no-clean', action='store_true', help='Skip cleaning before build')
    
    args = parser.parse_args()
    
    if args.clean:
        print("Cleaning build directories...")
        clean_build()
        print("Done.")
        return
    
    print("=" * 50)
    print("L3P Build Script")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    print("=" * 50 + "\n")
    
    if not args.no_clean:
        print("Cleaning previous build...")
        clean_build()
    
    build_executable()


if __name__ == '__main__':
    main()