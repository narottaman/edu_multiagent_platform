.PHONY: install test lint run compose-up compose-down zip
install:
	python -m pip install -e '.[dev,ui]'
test:
	pytest -q
lint:
	ruff check app tests
run:
	uvicorn app.api.main:app --reload
compose-up:
	docker compose up --build
compose-down:
	docker compose down
zip:
	cd .. && zip -r edu_multiagent_platform.zip edu_multiagent_platform -x 'edu_multiagent_platform/.env' '*/.git/*' '*/.venv/*'
