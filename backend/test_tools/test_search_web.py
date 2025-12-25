import sys
import os

# Add the project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.tools.search_web import search_web

results = search_web(
    query="what is the @overload decorator in python",
    max_results=5
)

# print(results)

for r in results:
    print(r["title"])
    print(r["url"])
    print(r["snippet"])
    print("----")

