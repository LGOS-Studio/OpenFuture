from pathlib import Path
from typing import Any, Dict

from .fs import FileSystemEmulator


class VendorPartition:
    """模拟 vendor 分区，管理驱动、模块和硬件适配。"""

    def __init__(self, vendor_path: Path, fs: FileSystemEmulator) -> None:
        self.vendor_path = vendor_path
        self.fs = fs
        self.metadata_path = vendor_path / "vendor.json"
        # 默认内置驱动：LGOS VirtIO 3.0.1
        self.data = {
            "drivers": {
                "virtio": {
                    "name": "LGOS VirtIO",
                    "version": "3.0.1",
                    "short": "virtio",
                    "vendor": "LGOS",
                    "description": "通用虚拟设备驱动（VirtIO），用于虚拟化环境的网络/块/控制器加速。",
                    "status": "installed",
                }
            },
            "modules": {},
            "hardware": {
                "gpu": "OpenFuture GPU",
                "network": "Virtual NIC",
            },
        }

    def initialize(self) -> None:
        self.fs.ensure_directory(self.vendor_path)
        # 创建驱动信息占位文件但不要覆盖已有文件
        drivers_info = self.vendor_path / "drivers.info"
        if not drivers_info.exists():
            self.fs.create_file(drivers_info, "# OpenFuture vendor partition\n")

        drivers_dir = self.vendor_path / "drivers"
        self.fs.ensure_directory(drivers_dir)

        # 如果已有 vendor.json，就加载而非覆盖
        if self.metadata_path.exists():
            data = self.fs.read_json(self.metadata_path)
            if data:
                self.data = data
        else:
            # 写入驱动详情文件（仅当首次初始化时写入）
            for name, spec in self.data.get("drivers", {}).items():
                try:
                    self.fs.write_json(drivers_dir / f"{name}.json", spec)
                except Exception:
                    pass
            self.fs.write_json(self.metadata_path, self.data)

    def install_module(self, module_name: str, module_data: Dict[str, Any]) -> None:
        modules = self.data.setdefault("modules", {})
        modules[module_name] = module_data
        self.sync()

    def install_driver(self, driver_name: str, driver_spec: Dict[str, Any]) -> None:
        drivers = self.data.setdefault("drivers", {})
        drivers[driver_name] = driver_spec
        self.sync()

    def remove_driver(self, driver_name: str) -> None:
        drivers = self.data.get("drivers", {})
        drivers.pop(driver_name, None)
        self.sync()

    def list_drivers(self) -> Dict[str, Any]:
        return self.data.get("drivers", {}).copy()

    def inspect(self) -> Dict[str, Any]:
        data = self.fs.read_json(self.metadata_path)
        if data:
            self.data = data
        return self.data.copy()

    def sync(self) -> None:
        self.fs.write_json(self.metadata_path, self.data)
