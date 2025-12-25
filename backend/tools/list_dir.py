from pathlib import Path
from typing import Dict, List, TypedDict


# Define a proper recursive type using TypedDict
class DirectoryTree(TypedDict):
    files: List[str]
    directories: Dict[str, "DirectoryTree"]

def list_dir(root_path: str) -> DirectoryTree:
    """
    Reads the structure of a directory without reading file contents.

    Args:
        root_path (str): Path to the root directory

    Returns:
        DirectoryTree: Nested dictionary representing folder structure
    """

    root = Path(root_path)

    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    def _walk(path: Path) -> DirectoryTree:
        structure: DirectoryTree = {
            "files": [], 
            "directories": {}
        }

        for item in sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
            if item.is_file():
                structure["files"].append(item.name)
            elif item.is_dir():
                structure["directories"][item.name] = _walk(item)

        return structure
    
    return _walk(root)