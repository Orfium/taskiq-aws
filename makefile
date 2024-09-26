up:
	docker compose up -d

down:
	docker compose down

test: up
	chmod +x ./wait-for-it.sh
	./wait-for-it.sh
	export AWS_ACCESS_KEY_ID=FAKE &&\
	export AWS_SECRET_ACCESS_KEY=FAKE &&\
	export AWS_ENDPOINT_URL=http://localhost:4566 &&\
	export TEST_SQS_QUEUE_URL=http://localhost:4566/000000000000/Queue &&\
	pytest

test-with-coverage-report: test
	poetry run coverage report

dep:
	pip install -r requirements-poetry.txt

install: dep
	poetry install --no-interaction --no-root

install-as-library: dep
	poetry install --no-interaction

pre-commit: install-as-library
	poetry run pre-commit run ${args}

publish-package: install-as-library
	poetry publish --build
