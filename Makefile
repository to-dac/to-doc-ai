.PHONY: specs test

specs:
	uv run python scripts/export_openapi.py

test:
	uv run pytest
