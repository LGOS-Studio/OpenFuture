import json
from pathlib import Path
from typing import Any, Dict

from .fs import FileSystemEmulator


class SystemPartition:
    """模拟 system 分区，管理系统服务和配置。"""

    def __init__(self, system_path: Path, fs: FileSystemEmulator) -> None:
        self.system_path = system_path
        self.fs = fs
        self.metadata_path = system_path / "system.json"
        self.data = {
            "properties": {
                "os.name": "OpenFuture",
                "os.version": "2.1.0.100",
                "build.type": "development",
            },
            "services": {},
        }

    def initialize(self) -> None:
        self.fs.ensure_directory(self.system_path)
        # 创建属性文件但不要覆盖已有文件
        build_prop = self.system_path / "build.prop"
        if not build_prop.exists():
            self.fs.create_file(build_prop, "# OpenFuture system properties\n")

        # 如果已有元数据，则加载而不是覆盖（保留运行时数据如 processes）
        if self.metadata_path.exists():
            data = self.fs.read_json(self.metadata_path)
            if data:
                self.data = data
        else:
            self.fs.write_json(self.metadata_path, self.data)

    def deploy_service(self, service_name: str, service_spec: Dict[str, Any]) -> None:
        services = self.data.setdefault("services", {})
        services[service_name] = service_spec
        self.sync()

    def remove_service(self, service_name: str) -> None:
        services = self.data.get("services", {})
        services.pop(service_name, None)
        self.sync()

    def list_services(self) -> Dict[str, Any]:
        return self.data.get("services", {}).copy()

    def set_property(self, key: str, value: Any) -> None:
        props = self.data.setdefault("properties", {})
        props[key] = value
        self.sync()
    # Process management removed — file system commands replace it

    def inspect(self) -> Dict[str, Any]:
        data = self.fs.read_json(self.metadata_path)
        if data:
            self.data = data
        return self.data.copy()

    def sync(self) -> None:
        self.fs.write_json(self.metadata_path, self.data)
