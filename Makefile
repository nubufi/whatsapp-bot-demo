.PHONY: run run_dev

run:
	uv run python main.py

run_dev:
	RELOAD=true uv run python main.py
