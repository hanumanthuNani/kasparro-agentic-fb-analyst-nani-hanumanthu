# -------------------------
# Kasparro Agentic FB Analyst
# Makefile for quick commands
# -------------------------

.PHONY: setup run test clean lint

# 1) Setup virtual environment + install deps
setup:
	python -m venv .venv
	.venv\Scripts\activate && pip install -r requirements.txt

# 2) Run pipeline (default example query)
run:
	.venv\Scripts\activate && python -m src.run "Analyze ROAS drop"

# 3) Run tests
test:
	.venv\Scripts\activate && pytest -q

# 4) Lint (optional if using flake8 or black)
lint:
	.venv\Scripts\activate && flake8 src/

# 5) Clean caches + reports
clean:
	del /Q /F /S __pycache__ 2>nul || true
	del /Q /F /S *.pyc 2>nul || true
	del /Q /F /S reports\* 2>nul || true
