import json
from pathlib import Path
from typing import Any, Dict, List


class FileSystemEmulator:
    """为 OpenFuture 提供根文件系统与元数据操作接口。"""

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def ensure_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def create_file(self, path: Path, content: str = "") -> None:
        self.ensure_directory(path.parent)
        path.write_text(content, encoding="utf-8")

    def write_json(self, path: Path, data: Dict[str, Any]) -> None:
        self.ensure_directory(path.parent)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def list_children(self, path: Path) -> List[str]:
        if not path.exists():
            return []
        return [child.name for child in path.iterdir()]

    def list_detailed(self, path: Path) -> List[dict]:
        """Return detailed listing for a directory."""
        results: List[dict] = []
        if not path.exists() or not path.is_dir():
            return results
        for child in path.iterdir():
            stat = child.stat()
            results.append(
                {
                    "name": child.name,
                    "is_dir": child.is_dir(),
                    "size": stat.st_size,
                    "mode": oct(stat.st_mode)[-3:],
                    "mtime": stat.st_mtime,
                }
            )
        return results

    def read_file(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def write_file(self, path: Path, content: str) -> None:
        self.ensure_directory(path.parent)
        path.write_text(content, encoding="utf-8")

    def delete(self, path: Path) -> None:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            for child in path.iterdir():
                self.delete(child)
            path.rmdir()

    def chmod(self, path: Path, mode: int) -> None:
        try:
            path.chmod(mode)
        except Exception:
            pass

    def exists(self, path: Path) -> bool:
        return path.exists()
