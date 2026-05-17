import shlex
import json
from typing import Any


class OpenFutureShell:
    """简单的交互式命令行，操作 OpenFuture 模拟系统。"""

    def __init__(self, os_sim) -> None:
        self.os = os_sim

    def _parse_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except Exception:
            return text

    def _help(self) -> None:
        print("可用命令:")
        print("  help                        - 显示本帮助")
        print("  partitions                  - 列出分区")
        print("  inspect <partition>         - 查看分区元数据 (boot/system/vendor)")
        print("  list_services               - 列出 system 中的服务")
        print("  list_drivers                - 列出 vendor 中的驱动")
        print("  ls [path]                   - 列出目录内容")
        print("  md|mkdir <path>             - 创建目录 (别名: md)")
        print("  chmod <mode> <path>         - 修改文件模式 (如 755)")
        print("  files                       - 启动交互式文件资源管理器")
        print("  set_boot <key> <json/value> - 设置 boot 元数据项 (value 可为 JSON)")
        print("  install_driver <name> <json>- 安装驱动 (spec JSON)")
        print("  install_module <name> <json> - 安装模块 (module 数据 JSON)")
        print("  deploy_service <name> <json> - 部署系统服务 (spec JSON)")
        print("  summary                     - 显示系统摘要")
        print("  boot                        - 执行引导并将引导日志写入 rootfs/boot/boot.log")
        # process management removed
        print("  sync                        - 保存所有分区元数据到 rootfs")
        print("  exit / quit                 - 退出交互式 shell")

    def start(self) -> None:
        print("Welcome to OpenFuture interactive shell. Type 'help'.")
        while True:
            try:
                raw = input("OpenFuture> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not raw:
                continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ("exit", "quit"):
                break
            if cmd == "help":
                self._help()
                continue
            if cmd == "partitions":
                print(self.os.list_partitions())
                continue
            if cmd == "inspect":
                if not args:
                    print("用法: inspect <partition>")
                    continue
                try:
                    print(self.os.inspect_partition(args[0]))
                except Exception as e:
                    print("错误:", e)
                continue
            if cmd == "list_services":
                print(self.os.system.list_services())
                continue
            if cmd == "list_drivers":
                print(self.os.vendor.list_drivers())
                continue
            if cmd == "set_boot":
                if len(args) < 2:
                    print("用法: set_boot <key> <json/value>")
                    continue
                key = args[0]
                value = self._parse_json(" ".join(args[1:]))
                self.os.set_boot_option(key, value)
                print("已设置")
                continue
            if cmd == "install_driver":
                if len(args) < 2:
                    print("用法: install_driver <name> <json>")
                    continue
                name = args[0]
                spec = self._parse_json(" ".join(args[1:]))
                if isinstance(spec, str):
                    print("驱动 spec 应为 JSON 对象或数组")
                    continue
                self.os.vendor.install_driver(name, spec)
                print("驱动已安装")
                continue
            if cmd == "install_module":
                if len(args) < 2:
                    print("用法: install_module <name> <json>")
                    continue
                name = args[0]
                data = self._parse_json(" ".join(args[1:]))
                if isinstance(data, str):
                    print("模块数据应为 JSON")
                    continue
                self.os.install_vendor_module(name, data)
                print("模块已安装")
                continue
            if cmd == "deploy_service":
                if len(args) < 2:
                    print("用法: deploy_service <name> <json>")
                    continue
                name = args[0]
                spec = self._parse_json(" ".join(args[1:]))
                if isinstance(spec, str):
                    print("服务 spec 应为 JSON")
                    continue
                self.os.load_system_service(name, spec)
                print("服务已部署")
                continue
            if cmd == "summary":
                print(self.os.summary())
                continue
            if cmd == "boot":
                # 默认将引导日志写入 boot.log
                out = self.os.boot_sequence(write_log=True)
                print(out)
                print("引导日志已写入 rootfs/boot/boot.log")
                continue
            if cmd in ("ls", "dir"):
                target = self.os.rootfs if not args else (self.os.rootfs / args[0]).resolve()
                try:
                    entries = self.os.fs.list_detailed(target)
                    for e in entries:
                        print(f"{('[D]' if e['is_dir'] else '[F]')} {e['name']} {e['size']} {e['mode']}")
                except Exception as e:
                    print("错误:", e)
                continue
            if cmd in ("md", "mkdir"):
                if not args:
                    print("用法: mkdir <path>")
                    continue
                target = (self.os.rootfs / args[0]).resolve()
                try:
                    target.mkdir(parents=True, exist_ok=True)
                    print("已创建")
                except Exception as e:
                    print("错误:", e)
                continue
            if cmd == "chmod":
                if len(args) < 2:
                    print("用法: chmod <mode> <path>")
                    continue
                mode_text = args[0]
                target = (self.os.rootfs / args[1]).resolve()
                try:
                    mode = int(mode_text, 8)
                    self.os.fs.chmod(target, mode)
                    print("模式已修改")
                except Exception as e:
                    print("错误:", e)
                continue
            if cmd == "files":
                try:
                    from .file_explorer import FileExplorer

                    fe = FileExplorer(self.os.rootfs)
                    fe.start()
                except Exception as e:
                    print("启动文件资源管理器失败:", e)
                continue
            if cmd == "sync":
                self.os.sync()
                print("已同步到 rootfs")
                continue

            print("未知命令: ", cmd)
