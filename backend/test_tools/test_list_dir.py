import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.list_dir import list_dir

structure = list_dir(root_path="backend")
print(structure)