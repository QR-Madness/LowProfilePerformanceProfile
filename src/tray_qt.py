# tray_qt.py
"""Qt-based system tray icon - works natively on KDE Plasma."""

import sys
from typing import Callable, Optional

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QImage, QPainter, QColor, QPixmap, QAction
from PyQt6.QtCore import QTimer, Qt

from .metrics import MetricsCollector
from .version import VERSION


class QtTrayIcon:
    """System tray icon using Qt - native support for KDE Plasma."""

    ICON_SIZE = 64
    PADDING = 4
    UPDATE_INTERVAL = 1000  # milliseconds

    def __init__(
        self,
        on_show_profile: Optional[Callable[[], None]] = None,
        on_exit: Optional[Callable[[], None]] = None
    ):
        """Initialize the Qt tray icon."""
        self._on_show_profile = on_show_profile
        self._on_exit = on_exit
        self._metrics = MetricsCollector()
        self._app: Optional[QApplication] = None
        self._tray: Optional[QSystemTrayIcon] = None
        self._timer: Optional[QTimer] = None
        
        # Calculate bar dimensions
        self._bar_width = (self.ICON_SIZE - self.PADDING * 4) // 3

    def _create_icon(self, cpu: float, mem: float, disk: float) -> QIcon:
        """Create a QIcon with the current metrics."""
        # Create image with solid background
        image = QImage(self.ICON_SIZE, self.ICON_SIZE, QImage.Format.Format_RGB32)
        image.fill(QColor(30, 30, 30))
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        values = [cpu, mem, disk]
        colors = [
            (QColor(0, 180, 0), QColor(0, 255, 0)),    # CPU - Green
            (QColor(180, 0, 0), QColor(255, 0, 0)),    # Mem - Red
            (QColor(0, 0, 180), QColor(0, 0, 255)),    # Disk - Blue
        ]
        
        bar_height = self.ICON_SIZE - 2 * self.PADDING
        
        for i, (value, (dark_color, bright_color)) in enumerate(zip(values, colors)):
            x = self.PADDING + i * (self._bar_width + self.PADDING)
            
            # Background
            painter.fillRect(
                x, self.PADDING,
                self._bar_width, bar_height,
                QColor(50, 50, 50)
            )
            
            # Usage bar
            usage_height = int(bar_height * value / 100)
            if usage_height > 0:
                y_start = self.ICON_SIZE - self.PADDING - usage_height
                
                # Simple gradient effect by interpolating colors
                for y in range(usage_height):
                    t = y / max(usage_height - 1, 1)
                    r = int(dark_color.red() + (bright_color.red() - dark_color.red()) * t)
                    g = int(dark_color.green() + (bright_color.green() - dark_color.green()) * t)
                    b = int(dark_color.blue() + (bright_color.blue() - dark_color.blue()) * t)
                    painter.setPen(QColor(r, g, b))
                    painter.drawLine(x, y_start + y, x + self._bar_width, y_start + y)
            
            # Outline
            painter.setPen(QColor(150, 150, 150))
            painter.drawRect(x, self.PADDING, self._bar_width, bar_height)
        
        painter.end()
        
        return QIcon(QPixmap.fromImage(image))

    def _update_metrics(self) -> None:
        """Update the tray icon with current metrics."""
        try:
            cpu, mem, disk = self._metrics.get_quick_metrics()
            
            # Update icon
            icon = self._create_icon(cpu, mem, disk)
            self._tray.setIcon(icon)
            
            # Update tooltip
            disk_label = "/" if sys.platform != "win32" else "C:"
            self._tray.setToolTip(
                f"L3P v{VERSION}\n"
                f"CPU: {cpu:.1f}%\n"
                f"Memory: {mem:.1f}%\n"
                f"Disk ({disk_label}): {disk:.1f}%"
            )
        except Exception as e:
            print(f"Update error: {e}", file=sys.stderr)

    def _handle_show_profile(self) -> None:
        """Handle Show Profile action."""
        if self._on_show_profile:
            self._on_show_profile()

    def _handle_exit(self) -> None:
        """Handle Exit action."""
        self.stop()
        if self._on_exit:
            self._on_exit()

    def run(self) -> None:
        """Run the tray icon (blocking)."""
        # Create Qt application if not exists
        self._app = QApplication.instance()
        if self._app is None:
            self._app = QApplication(sys.argv)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available!", file=sys.stderr)
            return
        
        # Create tray icon
        initial_icon = self._create_icon(25, 25, 25)
        self._tray = QSystemTrayIcon(initial_icon)
        self._tray.setToolTip("L3P - Loading...")
        
        # Create context menu
        menu = QMenu()
        
        if self._on_show_profile:
            show_action = QAction("Show Profile", menu)
            show_action.triggered.connect(self._handle_show_profile)
            menu.addAction(show_action)
            menu.addSeparator()
        
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self._handle_exit)
        menu.addAction(exit_action)
        
        self._tray.setContextMenu(menu)
        self._tray.show()
        
        # Start update timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_metrics)
        self._timer.start(self.UPDATE_INTERVAL)
        
        # Initial update
        self._update_metrics()
        
        # Run event loop
        self._app.exec()

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._timer:
            self._timer.stop()
        if self._tray:
            self._tray.hide()
        if self._app:
            self._app.quit()

    @property
    def is_running(self) -> bool:
        """Check if running."""
        return self._tray is not None and self._tray.isVisible()
