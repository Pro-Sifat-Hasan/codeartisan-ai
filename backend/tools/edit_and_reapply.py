from pathlib import Path
from typing import Dict, Union

def edit_and_reapply(
        file_path: str,
        start_line: int,
        end_line: int,
        new_code: str,
        *, 
        create_backup: bool = True
) -> Dict[str, Union[str, int, bool]]:
    
     """
    Edit a file by replacing a line range and reapply changes automatically.

    Args:
        file_path (str): Path to the file
        start_line (int): Start line number (1-based, inclusive)
        end_line (int): End line number (1-based, inclusive)
        new_code (str): Replacement code
        create_backup (bool): Whether to create a .bak file

    Returns:
        dict: Summary of changes
    """

     path = Path(file_path)

     if not path.exists:
          raise FileNotFoundError(f"File not found: {path}")
     
     if start_line < 1 or end_line < start_line:
          raise ValueError("Invalid line range")
     
     original_lines = path.read_text(encoding="utf-8").splitlines(keepends=True)

 
     if start_line > len(original_lines):
          raise ValueError("start line exceeds file length")
     
     # Backup
     if create_backup:
          backup_path = path.with_suffix(path.suffix + ".bak")
          backup_path.write_text("".join(original_lines), encoding="utf-8")
    
     # Prepare replacement
     new_lines = new_code.splitlines(keepends=True)
     if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] += "\n"

     # Apply edit
     updated_lines = (
          original_lines[: start_line - 1]
          + new_lines
          + original_lines[end_line:]
     )

     path.write_text("".join(updated_lines), encoding="utf-8")

     return {
          "file": str(path),
          "lines_replaced": f"{start_line}-{end_line}",
          "old_line_count": end_line - start_line + 1,
          "new_line_count": len(new_lines),
          "backup_created": str(create_backup),
     }

