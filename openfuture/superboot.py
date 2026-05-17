from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from .boot import BootManager


class SuperBoot:
    """一个更详细的引导加载器，模拟启动检查、内核加载与服务启动。"""

    def __init__(self, manager: "BootManager") -> None:
        self.manager = manager
        self.fs = manager.fs
        self.boot_path = manager.boot_path
        self.metadata_path = manager.metadata_path
        self.data = manager.data

    def _preflight_checks(self) -> List[str]:
        checks: List[str] = []
        if not self.boot_path.exists():
            checks.append("[FAIL] boot 分区不存在")
        else:
            checks.append("[OK] boot 分区存在")

        kernel = self.data.get("kernel")
        if kernel:
            checks.append(f"[OK] 发现内核: {kernel}")
        else:
            checks.append("[WARN] 未指定内核")

        return checks

    def _verify_kernel(self) -> str:
        # 模拟内核签名/完整性检查
        return "[OK] 内核签名验证 (模拟)"

    def _load_kernel(self) -> str:
        kernel = self.data.get("kernel", "<none>")
        return f"加载内核镜像: {kernel}"

    def _mount_rootfs(self) -> str:
        return f"挂载 rootfs: {self.fs.root_path}"

    def _start_services(self) -> str:
        services = self.data.get("services", [])
        if not services:
            return "没有要启动的服务"
        return f"启动服务: {services}"

    def run(self, write_log: bool = False) -> str:
        # 重新读取元数据，确保和磁盘同步
        self.data = self.fs.read_json(self.metadata_path) or self.data

        lines: List[str] = []
        # 如果存在 recovery flag，则进入恢复模式
        recovery_flag = self.fs.root_path / "recovery.flag"
        in_recovery = False
        try:
            if recovery_flag.exists():
                in_recovery = True
        except Exception:
            in_recovery = False

        lines.append("=== SuperBoot 启动序列 ===")
        if in_recovery:
            lines.append("[RECOVERY] 检测到 Recovery 模式标志，进入恢复模式")
        lines.extend(self._preflight_checks())
        lines.append(self._verify_kernel())
        lines.append(self._load_kernel())
        lines.append(self._mount_rootfs())
        # 如果处于恢复模式，仅启动最小恢复服务
        if in_recovery:
            lines.append("启动恢复服务: [recovery, logger]")
        else:
            lines.append(self._start_services())
        lines.append("=== SuperBoot 启动完成 ===")
        output = "\n".join(lines)

        if write_log:
            try:
                boot_log = self.boot_path / "boot.log"
                existing = ""
                try:
                    existing = self.fs.read_file(boot_log)
                except Exception:
                    existing = ""
                new_content = (existing + "\n\n" + output).strip()
                self.fs.write_file(boot_log, new_content)
            except Exception:
                # 写日志失败不影响引导输出
                pass

        return output
