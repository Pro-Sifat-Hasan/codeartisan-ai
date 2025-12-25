import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.read_file import read_file

content = read_file(file_path="backend/tools/read_file.py")
print(content)