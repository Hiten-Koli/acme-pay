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
    schema = json.dumps(create_app().openapi(), indent=2) + "\n"
    # LF on every OS, so the committed contract diffs cleanly against CI's export.
    target.write_text(schema, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
