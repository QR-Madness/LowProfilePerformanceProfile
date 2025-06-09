import dearpygui.dearpygui as dpg
import psutil
import time

class L3PProfile:
    def __init__(self):
        self.update_interval = 1.0  # Default update interval in seconds
        self.last_update = 0
        self.metrics = {"CPU": 0.0, "Memory": 0.0, "Disk": 0.0}

    def update_interval_callback(self, sender, data):
        self.update_interval = data

    def update_metrics(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            try:
                self.metrics["CPU"] = psutil.cpu_percent(interval=None)
                self.metrics["Memory"] = psutil.virtual_memory().percent
                self.metrics["Disk"] = psutil.disk_usage('/').percent

                # Update the UI elements
                dpg.set_value(self.cpu_text, f"CPU: {self.metrics['CPU']:.1f}%")
                dpg.set_value(self.mem_text, f"Memory: {self.metrics['Memory']:.1f}%")
                dpg.set_value(self.disk_text, f"Disk: {self.metrics['Disk']:.1f}%")

                self.last_update = current_time
            except Exception as e:
                print(f"Error updating metrics: {e}")

    def create_metrics_window(self):
        # Create the main window and store its tag
        self.main_window = dpg.add_window(label="System Metrics", pos=(10, 10))

        with dpg.window(tag=self.main_window):
            # Add update interval slider
            dpg.add_slider_float(
                label="Update Interval (seconds)",
                default_value=self.update_interval,
                min_value=0.1,
                max_value=5.0,
                callback=self.update_interval_callback
            )

            # Add metrics displays
            with dpg.group():
                self.cpu_text = dpg.add_text("CPU: 0.0%")
                self.mem_text = dpg.add_text("Memory: 0.0%")
                self.disk_text = dpg.add_text("Disk: 0.0%")

    def run(self):
        dpg.create_context()

        self.create_metrics_window()

        # Register the update callback
        with dpg.handler_registry():
            # Add more handlers here if needed
            pass

        dpg.create_viewport(title='System Metrics', width=400, height=200)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        while dpg.is_dearpygui_running():
            self.update_metrics()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()
