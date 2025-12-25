import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.read_code import read_code

codes = read_code(file_path="backend/tools/read_code.py", start_line=1, end_line=5)

print(codes)

