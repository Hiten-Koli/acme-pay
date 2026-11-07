"""Write the API's OpenAPI schema to a file (the frontend generates its types from it).

Usage (from backend/): uv run python scripts/export_openapi.py ../frontend/src/api/openapi.json
"""

import json
import sys
from pathlib import Path

from acme_pay.main import create_app


def main() -> None:
    """Export the schema to the path given as the first argument."""
    target = Path(sys.argv[1])
    target.write_text(json.dumps(create_app().openapi(), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
