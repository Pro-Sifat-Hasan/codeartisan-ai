import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.fetch_url_content import fetch_url_content

content = fetch_url_content(
    "https://typing.python.org/en/latest/spec/overload.html"
)

print(content)