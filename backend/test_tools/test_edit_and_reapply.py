import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.edit_and_reapply import edit_and_reapply

result = edit_and_reapply(
    file_path="fake.py",
    start_line=1,
    end_line=5,
    new_code="""
def read_code(file_path: str, start_line: int, end_line: int) -> str:
    \"\"\"Read code safely by line range. sifat\"\"\"
""".lstrip()
)