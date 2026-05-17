import json
from pathlib import Path
from typing import Any, Dict, List

from .fs import FileSystemEmulator
from .superboot import SuperBoot


class BootManager:
    """模拟引导分区管理。现在使用 SuperBoot 进行更丰富的启动序列模拟。"""

    def __init__(self, boot_path: Path, fs: FileSystemEmulator) -> None:
        self.boot_path = boot_path
        self.fs = fs
        self.metadata_path = boot_path / "boot.json"
        self.data = {
            "kernel": "openfuture-kernel.img",
            "bootargs": ["root=/dev/rootfs", "console=tty0"],
            "services": ["init", "logger", "network"],
            "kernels": ["openfuture-kernel.img"],
        }

    def initialize(self) -> None:
        self.fs.ensure_directory(self.boot_path)
        # 创建引导文件但不要覆盖已有文件
        boot_ini = self.boot_path / "boot.ini"
        if not boot_ini.exists():
            self.fs.create_file(boot_ini, "# OpenFuture boot partition\n")

        # 仅在没有元数据时写入默认元数据，防止覆盖运行时更改
        if self.metadata_path.exists():
            data = self.fs.read_json(self.metadata_path)
            if data:
                self.data = data
        else:
            self.fs.write_json(self.metadata_path, self.data)

    def boot(self, write_log: bool = False) -> str:
        # 使用 SuperBoot 执行详细的引导流程
        self.data = self.fs.read_json(self.metadata_path) or self.data
        loader = SuperBoot(self)
        return loader.run(write_log=write_log)

    def set_option(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.sync()

    def add_kernel(self, kernel_name: str) -> None:
        kernels = self.data.setdefault("kernels", [])
        if kernel_name not in kernels:
            kernels.append(kernel_name)
            self.sync()

    def list_kernels(self) -> List[str]:
        return self.data.get("kernels", [])

    def inspect(self) -> Dict[str, Any]:
        data = self.fs.read_json(self.metadata_path)
        if data:
            self.data = data
        return self.data.copy()

    def sync(self) -> None:
        self.fs.write_json(self.metadata_path, self.data)
