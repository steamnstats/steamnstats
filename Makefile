.PHONY: test-backend test-frontend lint-backend lint-frontend migrate

test-backend:
	cd backend && uv run pytest

test-frontend:
	cd frontend && npm test -- --run

lint-backend:
	cd backend && uv run ruff check app tests && uv run mypy app

lint-frontend:
	cd frontend && npm run lint

migrate:
	cd backend && uv run alembic upgrade head
