import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.terminal import run_terminal

result = run_terminal("python fake.py", cwd="backend")
print(result)
