from __future__ import annotations

from typing import Any, Callable, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from .core import OpenFutureOS


class OpenFutureInterface:
    """为开发者提供可扩展的 OpenFuture 插件与回调接口。"""

    def __init__(self, os_core: OpenFutureOS) -> None:
        self.os_core = os_core
        self.hooks: Dict[str, List[Callable[..., Any]]] = {
            "before_boot": [],
            "after_boot": [],
            "service_deploy": [],
            "module_install": [],
        }

    def register_hook(self, event_name: str, callback: Callable[..., Any]) -> None:
        if event_name not in self.hooks:
            raise ValueError(f"未知 hook 事件: {event_name}")
        self.hooks[event_name].append(callback)

    def trigger(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        for callback in self.hooks.get(event_name, []):
            callback(*args, **kwargs)

    def add_system_property(self, key: str, value: Any) -> None:
        self.os_core.system.set_property(key, value)

    def add_vendor_driver(self, name: str, spec: Dict[str, Any]) -> None:
        self.os_core.vendor.install_driver(name, spec)

    def add_service(self, name: str, spec: Dict[str, Any]) -> None:
        self.os_core.system.deploy_service(name, spec)
