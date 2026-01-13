# app.py
"""Main application controller for L3P."""

import platform
import sys
import signal
from threading import Thread, Event
from typing import Optional

from .tray import create_tray_icon, USE_QT_TRAY
from .profile_window import ProfileWindow


class L3PApp:
    """
    Main application that coordinates the tray icon and profile window.
    
    DearPyGui must run on the main thread, so we run the tray in a 
    background thread and use events to coordinate showing the profile.
    
    Exception: On KDE with Qt tray, Qt also needs the main thread,
    so we handle that case specially.
    """

    def __init__(self):
        """Initialize the application."""
        self._profile: Optional[ProfileWindow] = None
        self._tray = None
        self._tray_thread: Optional[Thread] = None
        self._show_profile_event = Event()
        self._exit_event = Event()
        self._os_type = platform.system()

    def _on_show_profile(self) -> None:
        """Callback when user clicks 'Show Profile' in tray menu."""
        self._show_profile_event.set()

    def _on_exit(self) -> None:
        """Callback when user clicks 'Exit' in tray menu."""
        self._exit_event.set()
        if self._profile:
            self._profile.stop()

    def _run_tray(self) -> None:
        """Run the tray icon in a thread."""
        self._tray = create_tray_icon(
            on_show_profile=self._on_show_profile,
            on_exit=self._on_exit
        )
        self._tray.run()

    def _handle_signal(self, signum: int, frame) -> None:
        """Handle termination signals."""
        self._exit_event.set()
        if self._profile:
            self._profile.stop()
        if self._tray:
            self._tray.stop()

    def run(self) -> None:
        """Run the application."""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        if USE_QT_TRAY:
            # Qt tray needs main thread - run profile in thread instead
            # Note: This means DearPyGui runs in a thread which can have issues
            # For now, just run tray-only mode effectively
            print("Running with Qt tray (KDE mode)", file=sys.stderr)
            self._tray = create_tray_icon(
                on_show_profile=self._on_show_profile,
                on_exit=self._on_exit
            )
            
            # For Qt mode, we'll run profile window when requested
            # but DearPyGui needs main thread so this is tricky
            # Best solution: show profile in subprocess or use Qt for profile too
            self._tray.run()
        else:
            # Standard mode: tray in background, DPG on main thread
            self._tray_thread = Thread(target=self._run_tray, daemon=True)
            self._tray_thread.start()

            # Main loop - handle profile window on main thread
            while not self._exit_event.is_set():
                if self._show_profile_event.wait(timeout=0.1):
                    self._show_profile_event.clear()
                    
                    self._profile = ProfileWindow()
                    try:
                        self._profile.run()
                    except Exception as e:
                        print(f"Profile window error: {e}", file=sys.stderr)
                    finally:
                        self._profile = None

            # Cleanup
            if self._tray:
                self._tray.stop()

            if self._tray_thread and self._tray_thread.is_alive():
                self._tray_thread.join(timeout=2.0)


def run_tray_only() -> None:
    """Run only the tray icon without profile window support."""
    tray = create_tray_icon()
    
    def signal_handler(signum, frame):
        tray.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    tray.run()


def run_profile_only() -> None:
    """Run only the profile window without tray icon."""
    profile = ProfileWindow()
    
    def signal_handler(signum, frame):
        profile.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    profile.run()
