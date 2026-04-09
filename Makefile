.DEFAULT_GOAL := help

.PHONY: help install dev test lint format run

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	uv sync --no-dev

dev: ## Install all dependencies including dev
	uv sync

test: ## Run test suite
	uv run pytest -v

lint: ## Lint with ruff
	uv run ruff check src tests

format: ## Format with ruff
	uv run ruff format src tests

run: ## Start the proxy server (hot-reload)
	uv run serve
