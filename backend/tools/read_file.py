from pathlib import Path

def read_file(file_path: str) -> str:
    """
    Reads the entire content of a file and returns it as a string.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Content of the file

    Raises:
        FileNotFoundError: If the file does not exist
    """

    # Use a different variable name
    path_obj = Path(file_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"File not found: {path_obj}")

    with open(path_obj, "r", encoding="utf-8") as file:
        content = file.read()

    return content