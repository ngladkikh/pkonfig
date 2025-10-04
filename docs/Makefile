# Makefile for Sphinx documentation tasks (included by the root Makefile)

# Directory containing Sphinx sources when invoked from repo root
DOCS_DIR ?= docs

.PHONY: docs-install docs-clean docs-build docs-linkcheck docs-serve docs

docs-install: ## Install documentation dependencies (Poetry group 'docs')
	poetry install --with docs

docs-clean: ## Clean built documentation
	rm -rf $(DOCS_DIR)/_build

docs-build: docs-install ## Build HTML docs (warnings as errors)
	poetry run sphinx-build -b html -W --keep-going $(DOCS_DIR) $(DOCS_DIR)/_build/html

docs-linkcheck: docs-install ## Check links in the documentation
	poetry run sphinx-build -b linkcheck $(DOCS_DIR) $(DOCS_DIR)/_build/linkcheck

docs-serve: docs-build ## Serve built docs at http://localhost:8000
	python -m http.server -d $(DOCS_DIR)/_build/html 8000

docs: docs-build docs-linkcheck ## Build docs and run linkcheck
