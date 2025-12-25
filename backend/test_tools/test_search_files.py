import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.search_files import search_files

results = search_files(
    root_path="backend",
    query="tool",
    include_dirs=True
)

print(results)