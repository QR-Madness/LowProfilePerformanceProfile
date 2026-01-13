# profile_window.py
"""DearPyGui-based profile window for detailed system metrics."""

import time
from typing import Dict, Any, Optional

import dearpygui.dearpygui as dpg

from .metrics import MetricsCollector, format_bytes, format_uptime
from .version import VERSION


class ProfileWindow:
    """Detailed system metrics window using DearPyGui."""

    # Theme colors for each category
    CATEGORY_COLORS = {
        "CPU": (141, 40, 40, 255),       # Red
        "Memory": (40, 141, 40, 255),    # Green
        "Disk": (40, 40, 141, 255),      # Blue
        "Network": (141, 141, 40, 255),  # Yellow
        "Processes": (141, 40, 141, 255),  # Purple
        "System": (40, 141, 141, 255)    # Cyan
    }

    def __init__(self):
        """Initialize the profile window."""
        self._metrics = MetricsCollector()
        self._update_interval = 1.0
        self._last_update = 0.0
        self._running = False
        self._category_themes: Dict[str, int] = {}
        self._main_window: Optional[int] = None

    def _create_theme(self) -> int:
        """Create the global theme and category-specific themes."""
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Dark sci-fi background
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (15, 15, 20, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Text, (200, 200, 200, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Border, (40, 40, 50, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 30, 40, 255))
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 40, 55, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (80, 80, 100, 255))
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (100, 100, 130, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button, (50, 50, 70, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (70, 70, 95, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 90, 120, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (40, 40, 55, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (50, 50, 70, 255))
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (60, 60, 85, 255))
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)

        # Create themes for each category
        for category, color in self.CATEGORY_COLORS.items():
            with dpg.theme() as category_theme:
                with dpg.theme_component(dpg.mvAll):
                    # Slightly muted color for header background
                    bg_color = (color[0] // 3, color[1] // 3, color[2] // 3, 255)
                    dpg.add_theme_color(dpg.mvThemeCol_Header, bg_color)
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, color)
                    dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, color)
            self._category_themes[category] = category_theme

        return global_theme

    def _on_interval_change(self, sender: int, value: float) -> None:
        """Handle update interval slider change."""
        self._update_interval = value

    def _create_metric_row(self, tag: str, label: str) -> None:
        """Create a single metric row with label and value."""
        with dpg.group(horizontal=True):
            dpg.add_text(f"{label}:", color=(150, 150, 150, 255))
            dpg.add_text("--", tag=tag)

    def _create_ui(self) -> None:
        """Create the main UI layout."""
        with dpg.window(label=f"L3P System Profile v{VERSION}", tag="main_window") as self._main_window:
            # Control section
            with dpg.group(horizontal=True):
                dpg.add_slider_float(
                    label="Update Interval",
                    default_value=self._update_interval,
                    format="%.1fs",
                    min_value=0.1,
                    max_value=5.0,
                    width=200,
                    callback=self._on_interval_change
                )
                dpg.add_spacer(width=20)
                dpg.add_button(
                    label="Close",
                    callback=lambda: dpg.stop_dearpygui(),
                    width=80
                )

            dpg.add_separator()
            dpg.add_spacer(height=5)

            # CPU Section
            with dpg.collapsing_header(label="CPU", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["CPU"])
                with dpg.group(indent=10):
                    self._create_metric_row("cpu_total", "Total Usage")
                    self._create_metric_row("cpu_cores", "Physical Cores")
                    self._create_metric_row("cpu_threads", "Logical Threads")
                    self._create_metric_row("cpu_freq", "Frequency")
                    self._create_metric_row("cpu_per_core", "Per Core")

            # Memory Section
            with dpg.collapsing_header(label="Memory", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["Memory"])
                with dpg.group(indent=10):
                    self._create_metric_row("mem_total", "Total")
                    self._create_metric_row("mem_available", "Available")
                    self._create_metric_row("mem_used", "Used")
                    self._create_metric_row("mem_swap", "Swap Used")

            # Disk Section
            with dpg.collapsing_header(label="Disk", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["Disk"])
                with dpg.group(indent=10):
                    self._create_metric_row("disk_mount", "Mount Point")
                    self._create_metric_row("disk_total", "Total")
                    self._create_metric_row("disk_used", "Used")
                    self._create_metric_row("disk_read", "Total Read")
                    self._create_metric_row("disk_write", "Total Write")

            # Network Section
            with dpg.collapsing_header(label="Network", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["Network"])
                with dpg.group(indent=10):
                    self._create_metric_row("net_sent", "Sent")
                    self._create_metric_row("net_recv", "Received")
                    self._create_metric_row("net_packets_sent", "Packets Sent")
                    self._create_metric_row("net_packets_recv", "Packets Received")

            # Processes Section
            with dpg.collapsing_header(label="Processes", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["Processes"])
                with dpg.group(indent=10):
                    self._create_metric_row("proc_total", "Total Processes")
                    self._create_metric_row("proc_cpu", "This Process CPU")
                    self._create_metric_row("proc_mem", "This Process Memory")
                    self._create_metric_row("proc_threads", "This Process Threads")

            # System Section
            with dpg.collapsing_header(label="System", default_open=True) as header:
                dpg.bind_item_theme(header, self._category_themes["System"])
                with dpg.group(indent=10):
                    self._create_metric_row("sys_hostname", "Hostname")
                    self._create_metric_row("sys_platform", "Platform")
                    self._create_metric_row("sys_boot", "Boot Time")
                    self._create_metric_row("sys_uptime", "Uptime")

    def _update_metrics(self) -> None:
        """Update all metric displays."""
        current_time = time.time()
        if current_time - self._last_update < self._update_interval:
            return

        try:
            # CPU
            cpu = self._metrics.get_cpu_metrics()
            dpg.set_value("cpu_total", f"{cpu.total_percent:.1f}%")
            dpg.set_value("cpu_cores", str(cpu.core_count))
            dpg.set_value("cpu_threads", str(cpu.thread_count))
            dpg.set_value("cpu_freq", f"{cpu.frequency_mhz:.0f} MHz")
            per_core_str = ", ".join(f"{p:.0f}%" for p in cpu.per_core_percent[:8])
            if len(cpu.per_core_percent) > 8:
                per_core_str += f" (+{len(cpu.per_core_percent) - 8} more)"
            dpg.set_value("cpu_per_core", per_core_str)

            # Memory
            mem = self._metrics.get_memory_metrics()
            dpg.set_value("mem_total", format_bytes(mem.total_bytes))
            dpg.set_value("mem_available", format_bytes(mem.available_bytes))
            dpg.set_value("mem_used", f"{mem.used_percent:.1f}%")
            dpg.set_value("mem_swap", f"{mem.swap_used_percent:.1f}%")

            # Disk
            disk = self._metrics.get_disk_metrics()
            dpg.set_value("disk_mount", disk.mount_point)
            dpg.set_value("disk_total", format_bytes(disk.total_bytes))
            dpg.set_value("disk_used", f"{disk.used_percent:.1f}%")
            dpg.set_value("disk_read", format_bytes(disk.read_bytes))
            dpg.set_value("disk_write", format_bytes(disk.write_bytes))

            # Network
            net = self._metrics.get_network_metrics()
            dpg.set_value("net_sent", format_bytes(net.bytes_sent))
            dpg.set_value("net_recv", format_bytes(net.bytes_recv))
            dpg.set_value("net_packets_sent", f"{net.packets_sent:,}")
            dpg.set_value("net_packets_recv", f"{net.packets_recv:,}")

            # Processes
            proc = self._metrics.get_process_metrics()
            dpg.set_value("proc_total", str(proc.total_processes))
            dpg.set_value("proc_cpu", f"{proc.current_cpu_percent:.1f}%")
            dpg.set_value("proc_mem", f"{proc.current_memory_percent:.1f}%")
            dpg.set_value("proc_threads", str(proc.current_threads))

            # System
            sys_info = self._metrics.get_system_info()
            dpg.set_value("sys_hostname", sys_info.hostname)
            dpg.set_value("sys_platform", sys_info.platform[:50] + "..." if len(sys_info.platform) > 50 else sys_info.platform)
            dpg.set_value("sys_boot", sys_info.boot_time.strftime("%Y-%m-%d %H:%M:%S"))
            dpg.set_value("sys_uptime", format_uptime(sys_info.uptime_seconds))

            self._last_update = current_time

        except Exception as e:
            # Log error but continue running
            pass

    def run(self) -> None:
        """Run the profile window (blocking)."""
        self._running = True

        dpg.create_context()

        # Create and apply theme
        global_theme = self._create_theme()
        dpg.bind_theme(global_theme)

        # Create UI
        self._create_ui()

        # Create viewport
        dpg.create_viewport(
            title=f'L3P System Profile v{VERSION}',
            width=550,
            height=700,
            min_width=400,
            min_height=500
        )

        # Configure viewport
        dpg.set_global_font_scale(1.1)
        dpg.set_viewport_clear_color([10, 10, 15, 255])

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main_window", True)

        # Main loop
        while dpg.is_dearpygui_running() and self._running:
            self._update_metrics()
            dpg.render_dearpygui_frame()

        dpg.destroy_context()

    def stop(self) -> None:
        """Stop the profile window."""
        self._running = False
        try:
            dpg.stop_dearpygui()
        except Exception:
            pass
