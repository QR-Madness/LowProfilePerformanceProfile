import sys
import psutil
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, Qt
from PIL import Image, ImageDraw

class SystemMetricsTray:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Create the system tray icon
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setIcon(QIcon('icon.png'))  # Replace with your icon path
        self.tray_icon.setVisible(True)

        # Create the menu
        self.menu = QMenu()
        self.exit_action = QAction('Exit', self.app)
        self.exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.menu)

        # Create a timer to refresh metrics
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_icon)
        self.timer.start(1000)  # Refresh every second

        # Start the app
        sys.exit(self.app.exec_())

    def update_icon(self):
        cpu_usage = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        mem_usage = mem.percent

        # Create an icon based on CPU and Memory usage
        icon = self.create_icon(cpu_usage, mem_usage)
        self.tray_icon.setIcon(QIcon(icon))

    def create_icon(self, cpu, mem):
        # Create an image for the icon
        width, height = 64, 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Draw CPU usage
        draw.rectangle([(0, height - cpu), (width / 2, height)], fill=(0, 255, 0))

        # Draw Memory usage
        draw.rectangle([(width / 2, height - mem), (width, height)], fill=(255, 0, 0))

        # Save the image as an icon
        icon_path = 'system_icon.png'
        image.save(icon_path)
        return icon_path

    def exit_app(self):
        self.tray_icon.hide()
        self.app.quit()

if __name__ == '__main__':
    SystemMetricsTray()
