# tray.py
"""Cross-platform system tray icon with metrics display."""

import os
import platform
import sys
from threading import Event, Thread
from typing import Callable, Optional, Tuple

from PIL import Image, ImageDraw

from .metrics import MetricsCollector
from .version import VERSION


def _should_use_qt() -> bool:
    """Check if we should use Qt-based tray (for KDE)."""
    if platform.system() != 'Linux':
        return False
    
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    # KDE/Plasma works best with Qt
    if 'kde' in desktop or 'plasma' in desktop or 'lxqt' in desktop:
        try:
            from PyQt6.QtWidgets import QApplication
            return True
        except ImportError:
            pass
    
    return False


def _setup_linux_backend() -> str:
    """Configure the best pystray backend for Linux. Returns the backend name."""
    session_type = os.environ.get('XDG_SESSION_TYPE', 'x11')
    desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
    
    # Check available modules
    has_gi = False
    
    try:
        import gi
        has_gi = True
    except ImportError:
        pass
    
    # GNOME/Unity - prefer appindicator
    if 'gnome' in desktop or 'unity' in desktop:
        if has_gi:
            os.environ['PYSTRAY_BACKEND'] = 'appindicator'
            return 'appindicator'
    
    # Other desktops - try gtk if available, fallback to xorg
    if has_gi:
        os.environ['PYSTRAY_BACKEND'] = 'gtk'
        return 'gtk'
    
    if session_type == 'x11' or session_type == '':
        os.environ['PYSTRAY_BACKEND'] = 'xorg'
        return 'xorg'
    
    return 'auto'


# Check if we should use Qt tray
USE_QT_TRAY = _should_use_qt()

# Configure pystray backend if not using Qt
if not USE_QT_TRAY and platform.system() == 'Linux':
    _setup_linux_backend()


class PystrayTrayIcon:
    """System tray icon using pystray library."""

    ICON_SIZE = (64, 64)
    PADDING = 4
    UPDATE_INTERVAL = 1.0

    def __init__(
        self,
        on_show_profile: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None
    ):
        import pystray
        self._pystray = pystray
        
        self._os_type = platform.system()
        self._stop_event = Event()
        self._on_show_profile = on_show_profile
        self._on_exit = on_exit
        self._metrics = MetricsCollector()
        self._bar_width = (self.ICON_SIZE[0] - self.PADDING * 4) // 3
        
        self._gradients = {
            'cpu': self._generate_gradient((0, 180, 0), (0, 255, 0)),
            'mem': self._generate_gradient((180, 0, 0), (255, 0, 0)),
            'disk': self._generate_gradient((0, 0, 180), (0, 0, 255)),
        }

        initial_icon = self._create_icon(25, 25, 25)
        
        self._icon = pystray.Icon(
            name="L3P",
            icon=initial_icon,
            title="L3P - Loading...",
            menu=self._create_menu()
        )
        self._update_thread: Optional[Thread] = None

    def _generate_gradient(self, start: Tuple[int, int, int], end: Tuple[int, int, int]):
        height = self.ICON_SIZE[1]
        return tuple(
            (
                int(start[0] + (end[0] - start[0]) * i / height),
                int(start[1] + (end[1] - start[1]) * i / height),
                int(start[2] + (end[2] - start[2]) * i / height),
                255
            )
            for i in range(height)
        )

    def _create_menu(self):
        menu_items = []
        if self._on_show_profile:
            menu_items.append(self._pystray.MenuItem("Show Profile", self._handle_show_profile))
            menu_items.append(self._pystray.Menu.SEPARATOR)
        menu_items.append(self._pystray.MenuItem("Exit", self._handle_exit))
        return self._pystray.Menu(*menu_items)

    def _handle_show_profile(self, icon, item):
        if self._on_show_profile:
            self._on_show_profile()

    def _handle_exit(self, icon, item):
        self.stop()
        if self._on_exit:
            self._on_exit()

    def _draw_bar(self, draw, index: int, usage: float, gradient):
        x = self.PADDING + index * (self._bar_width + self.PADDING)
        bar_height = self.ICON_SIZE[1] - 2 * self.PADDING
        usage_height = int(bar_height * usage / 100)

        if usage_height > 0:
            y_start = self.ICON_SIZE[1] - self.PADDING - usage_height
            for y in range(usage_height):
                gradient_idx = min(y, len(gradient) - 1)
                draw.line(
                    [(x, y_start + y), (x + self._bar_width, y_start + y)],
                    fill=gradient[gradient_idx],
                    width=1
                )

    def _create_icon(self, cpu: float, mem: float, disk: float) -> Image.Image:
        image = Image.new('RGB', self.ICON_SIZE, (30, 30, 30))
        draw = ImageDraw.Draw(image)

        for i in range(3):
            x = self.PADDING + i * (self._bar_width + self.PADDING)
            draw.rectangle(
                [(x, self.PADDING), (x + self._bar_width, self.ICON_SIZE[1] - self.PADDING)],
                fill=(50, 50, 50),
                outline=(100, 100, 100)
            )

        self._draw_bar(draw, 0, cpu, self._gradients['cpu'])
        self._draw_bar(draw, 1, mem, self._gradients['mem'])
        self._draw_bar(draw, 2, disk, self._gradients['disk'])

        for i in range(3):
            x = self.PADDING + i * (self._bar_width + self.PADDING)
            draw.rectangle(
                [(x, self.PADDING), (x + self._bar_width, self.ICON_SIZE[1] - self.PADDING)],
                outline=(150, 150, 150)
            )

        return image

    def _update_loop(self):
        self._stop_event.wait(0.5)
        
        while not self._stop_event.is_set():
            try:
                cpu, mem, disk = self._metrics.get_quick_metrics()
                self._icon.icon = self._create_icon(cpu, mem, disk)
                
                disk_label = "C:" if self._os_type == "Windows" else "/"
                self._icon.title = (
                    f"L3P v{VERSION}\n"
                    f"CPU: {cpu:.1f}%\n"
                    f"Memory: {mem:.1f}%\n"
                    f"Disk ({disk_label}): {disk:.1f}%"
                )
            except Exception as e:
                print(f"Tray update error: {e}", file=sys.stderr)

            self._stop_event.wait(self.UPDATE_INTERVAL)

    def _on_setup(self, icon):
        icon.visible = True
        self._update_thread = Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()

    def run(self):
        self._icon.run(setup=self._on_setup)

    def run_detached(self):
        self._icon.run_detached(setup=self._on_setup)

    def stop(self):
        self._stop_event.set()
        try:
            self._icon.stop()
        except Exception:
            pass

    @property
    def is_running(self) -> bool:
        return not self._stop_event.is_set()


# Alias for backwards compatibility
TrayIcon = PystrayTrayIcon


def create_tray_icon(
    on_show_profile: Optional[Callable[[], None]] = None,
    on_exit: Optional[Callable[[], None]] = None
):
    """Create a tray icon using the best available backend."""
    if USE_QT_TRAY:
        from .tray_qt import QtTrayIcon
        return QtTrayIcon(on_show_profile=on_show_profile, on_exit=on_exit)
    return PystrayTrayIcon(on_show_profile=on_show_profile, on_exit=on_exit)
