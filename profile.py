import dearpygui.dearpygui as dpg
import psutil
import time
from datetime import datetime

class L3PProfile:
    def __init__(self):
        self.update_interval = 1.0
        self.last_update = 0
        self.metrics = {}
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
                label="Update Interval (seconds)",
                default_value=self.update_interval,
                min_value=0.1,
                max_value=5.0,
                callback=self.update_interval_callback
            )

            for category in self.metrics.keys():
                with dpg.collapsing_header(label=category):
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
        self.create_metrics_window()

        dpg.create_viewport(title='System Metrics', width=500, height=600)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        while dpg.is_dearpygui_running():
            self.update_metrics()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()
