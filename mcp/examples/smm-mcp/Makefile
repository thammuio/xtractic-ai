# SSM MCP Server Makefile
# Common operations using uv

.PHONY: help install test run clean lint format

help: ## Show this help message
	@echo "SSM MCP Server - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	uv sync

install-dev: ## Install development dependencies
	uv sync --dev

test: ## Run connection test
	uv run python test_connection_uv.py

test-smm: ## Run SMM connection tests
	cd Testing && uv run python run_tests.py

run: ## Run the MCP server
	uv run python -m ssm_mcp_server.server

run-script: ## Run using the shell script
	./run_mcp_server.sh

lint: ## Run linting
	uv run ruff check src/

format: ## Format code
	uv run ruff format src/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .venv/

setup: ## Initial setup (install uv if needed)
	@if ! command -v uv &> /dev/null; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "Please restart your shell or run: source ~/.bashrc"; \
	else \
		echo "uv is already installed"; \
	fi
	uv sync

check: ## Check if uv is installed
	@if command -v uv &> /dev/null; then \
		echo "✅ uv is installed"; \
		uv --version; \
	else \
		echo "❌ uv is not installed. Run 'make setup' to install it."; \
	fi
