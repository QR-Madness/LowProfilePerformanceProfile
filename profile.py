import time
from datetime import datetime

import dearpygui.dearpygui as dpg
import psutil


class L3PProfile:
    def __init__(self):
        self.main_window = None
        self.update_interval = 1.0
        self.last_update = 0
        self.metrics = {}
        self.tab_states = {}  # Store expansion states
        self.colors = {
            "CPU": (141, 40, 40, 255),  # Red theme
            "Memory": (40, 141, 40, 255),  # Green theme
            "Disk": (40, 40, 141, 255),  # Blue theme
            "Network": (141, 141, 40, 255),  # Yellow theme
            "Processes": (141, 40, 141, 255),  # Purple theme
            "System": (40, 141, 141, 255)  # Cyan theme
        }
        self.init_metrics()

    def init_metrics(self):
        self.metrics = {
            "CPU": {},
            "Memory": {},
            "Disk": {},
            "Network": {},
            "Processes": {},
            "System": {}
        }
        # Initialize tab states
        self.tab_states = {category: True for category in self.metrics.keys()}

    def header_callback(self, sender):
        # Update tab state when clicked
        category = dpg.get_item_label(sender)
        self.tab_states[category] = dpg.get_item_state(sender)

    def create_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Dark sci-fi background
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (40, 40, 50, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)

        # Create themes for each category
        self.category_themes = {}
        for category, color in self.colors.items():
            with dpg.theme() as category_theme:
                with dpg.theme_component(dpg.mvAll):
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, color)
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, color)
                    dpg.add_theme_color(dpg.mvThemeCol_Text, color)
            self.category_themes[category] = category_theme

        return global_theme

    def update_interval_callback(self, sender, data):
        self.update_interval = data

    def format_bytes(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"

    def update_metrics(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            try:
                # CPU Metrics
                cpu_freq = psutil.cpu_freq()
                self.metrics["CPU"] = {
                    "Total Usage": f"{psutil.cpu_percent(interval=None):.1f}%",
                    "Per Core": [f"{x:.1f}%" for x in psutil.cpu_percent(percpu=True)],
                    "Frequency": f"{cpu_freq.current:.0f}MHz",
                    "Threads": len(psutil.Process().threads())
                }

                # Memory Metrics
                vmem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                self.metrics["Memory"] = {
                    "Total": self.format_bytes(vmem.total),
                    "Available": self.format_bytes(vmem.available),
                    "Used": f"{vmem.percent:.1f}%",
                    "Swap Used": f"{swap.percent:.1f}%"
                }

                # Disk Metrics
                disk = psutil.disk_usage('/')
                disk_io = psutil.disk_io_counters()
                self.metrics["Disk"] = {
                    "Total": self.format_bytes(disk.total),
                    "Used": f"{disk.percent:.1f}%",
                    "Read": self.format_bytes(disk_io.read_bytes),
                    "Write": self.format_bytes(disk_io.write_bytes)
                }

                # Network Metrics
                net = psutil.net_io_counters()
                self.metrics["Network"] = {
                    "Sent": self.format_bytes(net.bytes_sent),
                    "Received": self.format_bytes(net.bytes_recv),
                    "Packets Sent": net.packets_sent,
                    "Packets Received": net.packets_recv
                }

                # Process Metrics
                process = psutil.Process()
                self.metrics["Processes"] = {
                    "Total": len(psutil.pids()),
                    "Current CPU": f"{process.cpu_percent():.1f}%",
                    "Current Memory": f"{process.memory_percent():.1f}%",
                    "Threads": len(process.threads())
                }

                # System Info
                boot_time = datetime.fromtimestamp(psutil.boot_time())
                uptime = datetime.now() - boot_time
                self.metrics["System"] = {
                    "Boot Time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Uptime": str(uptime).split('.')[0]
                }

                self.update_ui()
                self.last_update = current_time
            except Exception as e:
                print(f"Error updating metrics: {e}")

    def update_ui(self):
        for category, metrics in self.metrics.items():
            for key, value in metrics.items():
                if isinstance(value, list):
                    text = f"{key}: {', '.join(value)}"
                else:
                    text = f"{key}: {value}"
                dpg.set_value(f"{category}_{key}", text)

    def create_metrics_window(self):
        self.main_window = dpg.add_window(label="System Metrics", pos=(10, 10))

        with dpg.window(tag=self.main_window):
            dpg.add_slider_float(
                label="Update Interval",
                default_value=self.update_interval,
                format="%.1fs",
                min_value=0.1,
                max_value=5.0,
                callback=self.update_interval_callback
            )
            dpg.add_button(label="Font Manager", callback=lambda: dpg.show_font_manager())
            dpg.add_button(label="Close", callback=lambda: dpg.stop_dearpygui())

            for category in self.metrics.keys():
                with dpg.collapsing_header(label=category, default_open=self.tab_states[category],
                                           # FIXME this has to call a global method
                                           # callback=self.header_callback
                                           ) as header:
                    # Apply a category-specific theme
                    dpg.bind_item_theme(header, self.category_themes[category])

                    with dpg.group():
                        if category == "CPU":
                            dpg.add_text("", tag="CPU_Total Usage")
                            dpg.add_text("", tag="CPU_Per Core")
                            dpg.add_text("", tag="CPU_Frequency")
                            dpg.add_text("", tag="CPU_Threads")
                        elif category == "Memory":
                            dpg.add_text("", tag="Memory_Total")
                            dpg.add_text("", tag="Memory_Available")
                            dpg.add_text("", tag="Memory_Used")
                            dpg.add_text("", tag="Memory_Swap Used")
                        elif category == "Disk":
                            dpg.add_text("", tag="Disk_Total")
                            dpg.add_text("", tag="Disk_Used")
                            dpg.add_text("", tag="Disk_Read")
                            dpg.add_text("", tag="Disk_Write")
                        elif category == "Network":
                            dpg.add_text("", tag="Network_Sent")
                            dpg.add_text("", tag="Network_Received")
                            dpg.add_text("", tag="Network_Packets Sent")
                            dpg.add_text("", tag="Network_Packets Received")
                        elif category == "Processes":
                            dpg.add_text("", tag="Processes_Total")
                            dpg.add_text("", tag="Processes_Current CPU")
                            dpg.add_text("", tag="Processes_Current Memory")
                            dpg.add_text("", tag="Processes_Threads")
                        elif category == "System":
                            dpg.add_text("", tag="System_Boot Time")
                            dpg.add_text("", tag="System_Uptime")

    def run(self):
        dpg.create_context()

        # Create and apply a theme
        global_theme = self.create_theme()
        dpg.bind_theme(global_theme)

        self.create_metrics_window()

        dpg.create_viewport(title='System Metrics', width=600, height=800)

        # Set DPI scaling
        dpg.set_global_font_scale(1.2)  # Increase font size
        dpg.set_viewport_clear_color([10, 10, 15, 255])  # Dark sci-fi background

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        # Enable DPI awareness
        dpg.configure_viewport("System Metrics", dpi_awareness=True)

        while dpg.is_dearpygui_running():
            self.update_metrics()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()
