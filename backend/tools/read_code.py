from pathlib import Path
from typing import Union
from langchain_core.tools import tool # type: ignore

@tool
def read_code(file_path: Union[str, Path], start_line: int, end_line: int) -> str:
    """
    Returns the code between start_line and end_line (inclusive) from a file.

    Args:
        file_path (Union[str, Path]): Path to the file as string or Path object
        start_line (int): Starting line number (1-based)
        end_line (int): Ending line number (1-based)

    Returns:
        str: Extracted code as a single string

    Raises:
        ValueError: If line numbers are invalid
        FileNotFoundError: If file does not exist
    """

    # Convert to Path if it's a string
    if isinstance(file_path, str):
        file_path = Path(file_path)
    
    # Now file_path is definitely a Path object
    path_obj = file_path

    if start_line < 1 or end_line < 1:
        raise ValueError("Line numbers must be >= 1")

    if start_line > end_line:
        raise ValueError("start_line cannot be greater than end_line")

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")
    
    with open(path_obj, "r", encoding="utf-8") as file:
        lines = file.readlines()

    total_lines = len(lines)

    if start_line > total_lines:
        return ""  # No content available
    
    # Adjust for 0 based indexing
    start_index = start_line - 1
    end_index = min(end_line, total_lines)

    return "".join(lines[start_index:end_index])