.PHONY: help fmt unit lint check

help: ## Show this help with available targets
	@echo "Available make targets:" && echo
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_.-]+:.*##/ {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

fmt: ## Format code with Black and isort
	black . && \
	isort .

unit: ## Run unit tests
	pytest tests

lint: ## Run static analysis (mypy and pylint)
	mypy pkonfig && pylint pkonfig

check: fmt unit lint ## Run format, tests, and lint

# Include documentation targets from docs/Makefile (if present)
-include docs/Makefile
