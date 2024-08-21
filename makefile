up:
	docker compose up -d

down:
	docker compose down

test: up
	export AWS_ACCESS_KEY_ID=FAKE &&\
	export AWS_SECRET_ACCESS_KEY=FAKE &&\
	export AWS_ENDPOINT_URL=http://localhost:4566 &&\
	export TEST_SQS_QUEUE_URL=http://localhost:4566/000000000000/Queue &&\
	pytest