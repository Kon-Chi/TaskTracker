.PHONY: help install run-api run-ui test lint bandit audit radon qa clean

POETRY ?= poetry

help:
	@echo "Targets:"
	@echo "  install   Install deps into .venv (project-local)"
	@echo "  run-api   Run FastAPI (uvicorn) with reload"
	@echo "  run-ui    Run Streamlit UI"
	@echo "  lint      Run flake8"
	@echo "  test      Run pytest with coverage gate (>=75%)"
	@echo "  bandit    Run bandit security scan"
	@echo "  audit     Run pip-audit (uses workspace cache dir)"
	@echo "  radon     Run complexity + maintainability reports"
	@echo "  qa        Run lint + test + security + radon"
	@echo "  clean     Remove local artifacts (db, caches, reports)"

install:
	$(POETRY) install --no-root --extras dev

run-api:
	$(POETRY) run uvicorn src.main:app --reload

run-ui:
	$(POETRY) run streamlit run src/task_tracker/ui/app.py

lint:
	$(POETRY) run flake8 --jobs=1 src tests

test:
	$(POETRY) run pytest --cov=src --cov-report=term-missing --cov-fail-under=75

bandit:
	$(POETRY) run bandit -r src

audit:
	mkdir -p .cache/pip-audit
	$(POETRY) run pip-audit --cache-dir .cache/pip-audit

radon:
	$(POETRY) run radon cc -a -s src
	$(POETRY) run radon mi -s src

qa: lint test bandit audit radon

clean:
	rm -rf .cache .pytest_cache htmlcov .coverage test_task_tracker.db task_tracker.db
