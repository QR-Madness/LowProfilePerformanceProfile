import os
import sys
import subprocess
import shutil
import glob

def clean_build():
    """Clean up build directories"""
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
    """Build the executable"""
    try:
        # Install required packages
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)

        # Build command - using Python interpreter to run PyInstaller
        build_cmd = [
            sys.executable,
            '-m',
            'PyInstaller',
            '--name=l3p',
            '--onefile',
            '--noconsole',
            '--add-data=README.md;.',
            '--hidden-import=PIL._tkinter_finder',
            '__main__.py'
        ]

        # Add icon parameter only if icon exists
        if os.path.exists('app_icon.ico'):
            build_cmd.insert(-1, '--icon=app_icon.ico')

        # Execute build
        subprocess.run(build_cmd, check=True)

        print("\nBuild completed successfully!")
        print("\nExecutable can be found in the 'dist' directory")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
        sys.exit(1)

if __name__ == '__main__':
    print("Starting the build process...")
    clean_build()
    build_executable()