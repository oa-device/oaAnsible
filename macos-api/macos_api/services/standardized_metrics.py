"""
Standardized Metrics Service for macOS API

This service provides standardized health metrics that comply with the shared schemas.
"""

import platform
from datetime import datetime, timezone
from typing import Dict

import psutil

# Import local health schemas - self-contained for independent deployment
from ..models.health_schemas import (
    BaseCPUMetrics,
    BaseMemoryMetrics,
    BaseDiskMetrics,
    BaseNetworkMetrics,
    BaseHealthMetrics,
    BaseSystemInfo,
    BaseDeviceInfo,
    BaseVersionInfo,
    MacOSCapabilities
)

from ..core.config import APP_VERSION
from .system import get_version_info


def get_standardized_cpu_metrics() -> BaseCPUMetrics:
    """Get CPU metrics in standardized format."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count()
        
        # Get processor information
        version_info = get_version_info()
        cpu_model = version_info.get("processor", platform.processor())
        
        return BaseCPUMetrics(
            usage_percent=cpu_usage,
            cores=cpu_cores,
            architecture=platform.machine(),
            model=cpu_model
        )
    except Exception as e:
        # Fallback with minimal data
        return BaseCPUMetrics(
            usage_percent=psutil.cpu_percent(interval=0.1),
            cores=psutil.cpu_count() or 1,
            architecture=platform.machine(),
            model="Unknown"
        )


def get_standardized_memory_metrics() -> BaseMemoryMetrics:
    """Get memory metrics in standardized format."""
    try:
        memory = psutil.virtual_memory()
        
        return BaseMemoryMetrics(
            usage_percent=memory.percent,
            total=memory.total,
            used=memory.used,
            available=memory.available
        )
    except Exception as e:
        # Fallback with minimal data
        memory = psutil.virtual_memory()
        return BaseMemoryMetrics(
            usage_percent=memory.percent,
            total=memory.total,
            used=memory.used,
            available=memory.available
        )


def get_standardized_disk_metrics() -> BaseDiskMetrics:
    """Get disk metrics in standardized format."""
    try:
        disk = psutil.disk_usage("/")
        
        return BaseDiskMetrics(
            usage_percent=disk.percent,
            total=disk.total,
            used=disk.used,
            free=disk.free,
            path="/"
        )
    except Exception as e:
        # Fallback with minimal data
        disk = psutil.disk_usage("/")
        return BaseDiskMetrics(
            usage_percent=disk.percent,
            total=disk.total,
            used=disk.used,
            free=disk.free,
            path="/"
        )


def get_standardized_network_metrics() -> BaseNetworkMetrics:
    """Get network metrics in standardized format."""
    try:
        # Get aggregate network stats
        net_io = psutil.net_io_counters()
        if net_io:
            return BaseNetworkMetrics(
                bytes_sent=net_io.bytes_sent,
                bytes_received=net_io.bytes_recv,
                packets_sent=net_io.packets_sent,
                packets_received=net_io.packets_recv,
                interface="aggregate"
            )
        else:
            # Fallback to zero values
            return BaseNetworkMetrics(
                bytes_sent=0,
                bytes_received=0,
                packets_sent=0,
                packets_received=0,
                interface="unknown"
            )
    except Exception as e:
        # Fallback with zero values
        return BaseNetworkMetrics(
            bytes_sent=0,
            bytes_received=0,
            packets_sent=0,
            packets_received=0,
            interface="error"
        )


def get_standardized_health_metrics() -> BaseHealthMetrics:
    """Get complete standardized health metrics."""
    return BaseHealthMetrics(
        cpu=get_standardized_cpu_metrics(),
        memory=get_standardized_memory_metrics(),
        disk=get_standardized_disk_metrics(),
        network=get_standardized_network_metrics()
    )


def get_standardized_system_info() -> BaseSystemInfo:
    """Get system information in standardized format."""
    try:
        version_info = get_version_info()
        uptime_info = version_info.get("uptime", {})
        
        return BaseSystemInfo(
            os_version=version_info.get("macos_version", platform.release()),
            kernel_version=platform.release(),
            hostname=platform.node(),
            uptime=uptime_info.get("seconds"),
            uptime_human=uptime_info.get("formatted", "Unknown"),
            boot_time=psutil.boot_time(),
            architecture=platform.machine()
        )
    except Exception as e:
        return BaseSystemInfo(
            os_version=platform.release(),
            kernel_version=platform.release(),
            hostname=platform.node(),
            uptime=None,
            uptime_human="Unknown",
            boot_time=psutil.boot_time(),
            architecture=platform.machine()
        )


def get_standardized_device_info() -> BaseDeviceInfo:
    """Get device information in standardized format."""
    try:
        version_info = get_version_info()
        return BaseDeviceInfo(
            type="Mac",
            series="Mac Mini",
            hostname=platform.node(),
            model=version_info.get("product_name", "Mac")
        )
    except Exception as e:
        return BaseDeviceInfo(
            type="Mac",
            series="Mac Mini",
            hostname=platform.node(),
            model="Mac"
        )


def get_standardized_version_info() -> BaseVersionInfo:
    """Get version information in standardized format."""
    try:
        version_info = get_version_info()
        return BaseVersionInfo(
            api=APP_VERSION,
            python=platform.python_version(),
            tailscale=version_info.get("tailscale_version"),
            system={
                "platform": platform.system(),
                "release": platform.release(),
                "os": f"{platform.system()} {platform.release()}",
                "type": "Mac",
                "series": "Mac Mini"
            }
        )
    except Exception as e:
        return BaseVersionInfo(
            api=APP_VERSION,
            python=platform.python_version(),
            tailscale=None,
            system={
                "platform": platform.system(),
                "release": platform.release(),
                "os": f"{platform.system()} {platform.release()}",
                "type": "Mac",
                "series": "Mac Mini"
            }
        )


def get_standardized_capabilities() -> MacOSCapabilities:
    """Get macOS capabilities in standardized format."""
    return MacOSCapabilities(
        supports_camera_stream=True,
        supports_tracker_restart=True,
        supports_reboot=True,
        supports_ssh=True,
        device_has_camera_support=True
    )