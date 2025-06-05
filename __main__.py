import os
import platform
from functools import lru_cache
from threading import Event, Thread

import psutil
import pystray
from PIL import Image, ImageDraw

try:
    from version import VERSION, BUILD_DATE
except ImportError:
    VERSION = "dev"
    BUILD_DATE = "unknown"


class SystemMetricsTray:
    def __init__(self):
        self.os_type = platform.system()
        self.stop_event = Event()

        # Cache gradients to avoid recalculation
        self._gradient_cache = {
            'cpu': self._generate_gradient((0, 100, 0, 230), (0, 255, 0, 230)),
            'mem': self._generate_gradient((100, 0, 0, 230), (255, 0, 0, 230)),
            'disk': self._generate_gradient((0, 0, 100, 230), (0, 0, 255, 230)),
            'bg': self._generate_gradient((40, 40, 40, 100), (80, 80, 80, 100))
        }

        # Constants for icon creation
        self.ICON_SIZE = (64, 64)
        self.PADDING = 2
        self.BAR_WIDTH = (self.ICON_SIZE[0] - self.PADDING * 4) // 3

        # Create initial icon
        icon_image = self.create_icon(0, 0, 0)

        # Store system drive for repeated use
        self.system_drive = os.environ.get('SystemDrive', 'C:') if self.os_type == 'Windows' else '/'

        self.tray_icon = pystray.Icon(
            "System Metrics",
            icon_image,
            "System Metrics",
            menu=pystray.Menu(
                pystray.MenuItem("Exit", self.exit_app)
            )
        )

        self.update_thread = Thread(target=self.update_metrics, daemon=True)

    @staticmethod
    @lru_cache(maxsize=64)
    def _generate_gradient(start_color, end_color):
        """Generate and cache gradient colors"""
        height = 64  # Match icon height
        return tuple(
            (
                int(start_color[0] + (end_color[0] - start_color[0]) * i / height),
                int(start_color[1] + (end_color[1] - start_color[1]) * i / height),
                int(start_color[2] + (end_color[2] - start_color[2]) * i / height),
                int(start_color[3] + (end_color[3] - start_color[3]) * i / height)
            )
            for i in range(height)
        )

    def run(self):
        self.update_thread.start()
        self.tray_icon.run()

    def get_disk_usage(self):
        try:
            return psutil.disk_usage(self.system_drive).percent
        except:
            return 0.0

    def get_system_metrics(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().percent
            disk_usage = self.get_disk_usage()
            return cpu_usage, mem_usage, disk_usage
        except:
            return 0.0, 0.0, 0.0

    def draw_usage_bar(self, draw, index, usage, gradient_colors):
        x = self.PADDING + index * (self.BAR_WIDTH + self.PADDING)
        usage_height = int(((self.ICON_SIZE[1] - 2 * self.PADDING) * usage / 100))

        if usage_height > 0:
            y_start = self.ICON_SIZE[1] - self.PADDING - usage_height
            for y in range(usage_height):
                draw.line(
                    [(x, y_start + y), (x + self.BAR_WIDTH, y_start + y)],
                    fill=gradient_colors[y],
                    width=1
                )

    def create_icon(self, cpu, mem, disk):
        image = Image.new('RGBA', self.ICON_SIZE, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        # Draw background and outlines
        for i in range(3):
            x = self.PADDING + i * (self.BAR_WIDTH + self.PADDING)

            # Background
            for y in range(self.ICON_SIZE[1] - 2 * self.PADDING):
                draw.line(
                    [(x, y + self.PADDING), (x + self.BAR_WIDTH, y + self.PADDING)],
                    fill=self._gradient_cache['bg'][y],
                    width=1
                )

            # Outline
            draw.rectangle([
                (x, self.PADDING),
                (x + self.BAR_WIDTH, self.ICON_SIZE[1] - self.PADDING)
            ], outline=(128, 128, 128, 200))

        # Draw usage bars
        self.draw_usage_bar(draw, 0, cpu, self._gradient_cache['cpu'])
        self.draw_usage_bar(draw, 1, mem, self._gradient_cache['mem'])
        self.draw_usage_bar(draw, 2, disk, self._gradient_cache['disk'])

        return image

    def update_metrics(self):
        while not self.stop_event.is_set():
            cpu_usage, mem_usage, disk_usage = self.get_system_metrics()

            new_icon = self.create_icon(cpu_usage, mem_usage, disk_usage)
            self.tray_icon.icon = new_icon

            disk_label = "C:" if self.os_type == "Windows" else "/"
            self.tray_icon.title = (
                f"Low-Profile Performance Profile (L3P) v.{VERSION}\n"
                f"CPU: {cpu_usage:.1f}%\n"
                f"Memory: {mem_usage:.1f}%\n"
                f"Disk ({disk_label}): {disk_usage:.1f}%"
            )

            self.stop_event.wait(1)

    def exit_app(self):
        self.stop_event.set()
        self.tray_icon.stop()


if __name__ == '__main__':
    app = SystemMetricsTray()
    app.run()
