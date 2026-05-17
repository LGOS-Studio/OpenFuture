from pathlib import Path
from typing import Optional


class FileExplorer:
    """简单的文件资源管理器，用于交互式浏览 rootfs。"""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.cwd = self.root

    def _resolve(self, p: str) -> Path:
        ppath = Path(p)
        if ppath.is_absolute():
            return (self.root / ppath.relative_to(ppath.anchor)).resolve()
        return (self.cwd / ppath).resolve()

    def start(self) -> None:
        print(f"File Explorer — root: {self.root}")
        while True:
            try:
                cmd = input(f"files:{self.cwd.relative_to(self.root)}$ ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not cmd:
                continue
            parts = cmd.split()
            op = parts[0].lower()
            args = parts[1:]

            if op in ("exit", "quit", "q"):
                break
            if op == "ls":
                path = self.cwd if not args else self._resolve(args[0])
                if not path.exists():
                    print("路径不存在")
                    continue
                for child in sorted(path.iterdir()):
                    print(("[D]" if child.is_dir() else "[F]"), child.name)
                continue
            if op == "cd":
                if not args:
                    print("用法: cd <path>")
                    continue
                target = self._resolve(args[0])
                if not target.exists() or not target.is_dir():
                    print("目录不存在")
                    continue
                self.cwd = target
                continue
            if op == "cat":
                if not args:
                    print("用法: cat <file>")
                    continue
                target = self._resolve(args[0])
                if not target.exists() or not target.is_file():
                    print("文件不存在")
                    continue
                try:
                    print(target.read_text(encoding="utf-8"))
                except Exception:
                    print("无法读取文件")
                continue
            if op == "rm":
                if not args:
                    print("用法: rm <path>")
                    continue
                target = self._resolve(args[0])
                if not target.exists():
                    print("路径不存在")
                    continue
                try:
                    if target.is_dir():
                        for child in target.iterdir():
                            if child.is_file():
                                child.unlink()
                        target.rmdir()
                    else:
                        target.unlink()
                    print("已删除")
                except Exception as e:
                    print("删除失败:", e)
                continue
            if op == "mkdir":
                if not args:
                    print("用法: mkdir <dir>")
                    continue
                target = self._resolve(args[0])
                try:
                    target.mkdir(parents=True, exist_ok=True)
                    print("已创建")
                except Exception as e:
                    print("创建失败:", e)
                continue
            print("未知命令", op)