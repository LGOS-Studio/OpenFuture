from pathlib import Path
from typing import Any, Dict, List

from .boot import BootManager
from .fs import FileSystemEmulator
from .interface import OpenFutureInterface
from .system import SystemPartition
from .vendor import VendorPartition


class OpenFutureOS:
    """OpenFuture 模拟操作系统核心。"""

    def __init__(self, rootfs_path: str | Path | None = None) -> None:
        self.rootfs = Path(rootfs_path or Path.cwd() / "rootfs").resolve()
        self.fs = FileSystemEmulator(self.rootfs)
        self.boot = BootManager(self.rootfs / "boot", self.fs)
        self.system = SystemPartition(self.rootfs / "system", self.fs)
        self.vendor = VendorPartition(self.rootfs / "vendor", self.fs)
        self.interface = OpenFutureInterface(self)

    def initialize(self) -> None:
        """创建必要分区，并生成默认配置文件。"""
        self.fs.ensure_directory(self.rootfs)
        self.boot.initialize()
        self.system.initialize()
        self.vendor.initialize()

    def boot_sequence(self, write_log: bool = False) -> str:
        """执行模拟引导序列。"""
        return self.boot.boot(write_log=write_log)

    def set_boot_option(self, key: str, value: Any) -> None:
        self.boot.set_option(key, value)

    def install_vendor_module(self, module_name: str, module_data: Dict[str, Any]) -> None:
        self.vendor.install_module(module_name, module_data)

    def load_system_service(self, service_name: str, service_spec: Dict[str, Any]) -> None:
        self.system.deploy_service(service_name, service_spec)
    # Process management removed — commands replaced by file management

    def inspect_partition(self, partition_name: str) -> Dict[str, Any]:
        partition_name = partition_name.lower()
        if partition_name == "boot":
            return self.boot.inspect()
        if partition_name == "system":
            return self.system.inspect()
        if partition_name == "vendor":
            return self.vendor.inspect()
        raise ValueError(f"未知分区: {partition_name}")

    def list_partitions(self) -> List[str]:
        return ["boot", "system", "vendor"]

    def sync(self) -> None:
        """保存所有分区的当前状态到 rootfs。"""
        self.boot.sync()
        self.system.sync()
        self.vendor.sync()

    def summary(self) -> Dict[str, Any]:
        return {
            "rootfs": str(self.rootfs),
            "partitions": {
                "boot": self.boot.inspect(),
                "system": self.system.inspect(),
                "vendor": self.vendor.inspect(),
            },
        }
