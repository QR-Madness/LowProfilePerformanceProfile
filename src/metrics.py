# metrics.py
"""Cross-platform system metrics collection."""

import os
import platform
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import psutil


@dataclass
class CPUMetrics:
    """CPU usage metrics."""
    total_percent: float
    per_core_percent: List[float]
    frequency_mhz: float
    core_count: int
    thread_count: int


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""
    total_bytes: int
    available_bytes: int
    used_percent: float
    swap_total_bytes: int
    swap_used_percent: float


@dataclass
class DiskMetrics:
    """Disk usage metrics."""
    total_bytes: int
    used_percent: float
    read_bytes: int
    write_bytes: int
    mount_point: str


@dataclass
class NetworkMetrics:
    """Network I/O metrics."""
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int


@dataclass
class ProcessMetrics:
    """Process-related metrics."""
    total_processes: int
    current_cpu_percent: float
    current_memory_percent: float
    current_threads: int


@dataclass
class SystemInfo:
    """System information."""
    boot_time: datetime
    uptime_seconds: float
    platform: str
    hostname: str


class MetricsCollector:
    """Cross-platform system metrics collector."""

    def __init__(self):
        self._os_type = platform.system()
        self._system_drive = self._get_system_drive()
        self._process = psutil.Process()

    def _get_system_drive(self) -> str:
        """Get the system drive/mount point based on OS."""
        if self._os_type == 'Windows':
            return os.environ.get('SystemDrive', 'C:') + '\\'
        return '/'

    @property
    def os_type(self) -> str:
        """Get the operating system type."""
        return self._os_type

    @property
    def system_drive(self) -> str:
        """Get the system drive/mount point."""
        return self._system_drive

    def get_cpu_metrics(self) -> CPUMetrics:
        """Collect CPU metrics."""
        try:
            freq = psutil.cpu_freq()
            frequency = freq.current if freq else 0.0

            return CPUMetrics(
                total_percent=psutil.cpu_percent(interval=None),
                per_core_percent=psutil.cpu_percent(percpu=True),
                frequency_mhz=frequency,
                core_count=psutil.cpu_count(logical=False) or 1,
                thread_count=psutil.cpu_count(logical=True) or 1
            )
        except Exception:
            return CPUMetrics(0.0, [], 0.0, 1, 1)

    def get_memory_metrics(self) -> MemoryMetrics:
        """Collect memory metrics."""
        try:
            vmem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return MemoryMetrics(
                total_bytes=vmem.total,
                available_bytes=vmem.available,
                used_percent=vmem.percent,
                swap_total_bytes=swap.total,
                swap_used_percent=swap.percent
            )
        except Exception:
            return MemoryMetrics(0, 0, 0.0, 0, 0.0)

    def get_disk_metrics(self) -> DiskMetrics:
        """Collect disk metrics."""
        try:
            disk = psutil.disk_usage(self._system_drive)
            disk_io = psutil.disk_io_counters()

            return DiskMetrics(
                total_bytes=disk.total,
                used_percent=disk.percent,
                read_bytes=disk_io.read_bytes if disk_io else 0,
                write_bytes=disk_io.write_bytes if disk_io else 0,
                mount_point=self._system_drive
            )
        except Exception:
            return DiskMetrics(0, 0.0, 0, 0, self._system_drive)

    def get_network_metrics(self) -> NetworkMetrics:
        """Collect network metrics."""
        try:
            net = psutil.net_io_counters()
            return NetworkMetrics(
                bytes_sent=net.bytes_sent,
                bytes_recv=net.bytes_recv,
                packets_sent=net.packets_sent,
                packets_recv=net.packets_recv
            )
        except Exception:
            return NetworkMetrics(0, 0, 0, 0)

    def get_process_metrics(self) -> ProcessMetrics:
        """Collect process metrics."""
        try:
            return ProcessMetrics(
                total_processes=len(psutil.pids()),
                current_cpu_percent=self._process.cpu_percent(),
                current_memory_percent=self._process.memory_percent(),
                current_threads=len(self._process.threads())
            )
        except Exception:
            return ProcessMetrics(0, 0.0, 0.0, 0)

    def get_system_info(self) -> SystemInfo:
        """Collect system information."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = (datetime.now() - boot_time).total_seconds()

            return SystemInfo(
                boot_time=boot_time,
                uptime_seconds=uptime,
                platform=platform.platform(),
                hostname=platform.node()
            )
        except Exception:
            return SystemInfo(
                boot_time=datetime.now(),
                uptime_seconds=0.0,
                platform='Unknown',
                hostname='Unknown'
            )

    def get_quick_metrics(self) -> tuple[float, float, float]:
        """Get quick CPU, memory, and disk usage percentages for tray icon."""
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage(self._system_drive).percent
            return cpu, mem, disk
        except Exception:
            return 0.0, 0.0, 0.0


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024
    return f"{bytes_value:.1f} TB"


def format_uptime(seconds: float) -> str:
    """Format uptime in seconds to human-readable string."""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return ' '.join(parts)
