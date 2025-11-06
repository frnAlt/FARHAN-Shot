.PHONY: help install test run-dry convert-db clean lint

help:
	@echo "WPS Toolkit - Available Commands"
	@echo "================================="
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run unit tests with coverage"
	@echo "  make run-dry      - Run dry-run demo"
	@echo "  make convert-db   - Create sample vulnerability database"
	@echo "  make clean        - Clean temporary files"
	@echo "  make lint         - Run code quality checks"

install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

test:
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v
	@echo "✓ Tests completed - Coverage report in htmlcov/index.html"

run-dry:
	python3 main.py --dry-run --target 00:11:22:33:44:55 --pixie --bruteforce --verbose

convert-db:
	python3 tools/convert_vulnwsc.py --create-sample
	@echo "✓ Sample database created at db/vuln_db.json"

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ tools/__pycache__
	rm -rf .pytest_cache htmlcov .coverage
	rm -rf *.log
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✓ Cleaned temporary files"

lint:
	@echo "Running type checks..."
	@python3 -m py_compile main.py
	@python3 -m py_compile src/*.py
	@echo "✓ Type checks passed"
