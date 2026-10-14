"""Regenera el archivo JSON local del contrato OpenAPI v0."""

import json
from pathlib import Path

from openapi_v0 import app


destination = Path(__file__).parents[1] / "docs" / "spec" / "openapi-v0.json"
destination.write_text(
    json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"OpenAPI v0 written to {destination}")
