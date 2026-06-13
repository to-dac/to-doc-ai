"""Export the FastAPI OpenAPI schema to openapi.json."""

import json
from pathlib import Path


def main() -> None:
    from app.main import app

    spec = app.openapi()
    out = Path(__file__).resolve().parents[1] / "openapi.json"
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
