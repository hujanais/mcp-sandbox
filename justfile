ruff:
	uv run ruff check --fix .

format-ruff:
	uv run ruff format

format: format-ruff