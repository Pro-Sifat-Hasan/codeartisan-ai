import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.grep import grep

results = grep(
    pattern=r"def\s+\w+",
    root_path="backend",
    use_regex=True,
    file_extensions=[".py"]
)

print(results)