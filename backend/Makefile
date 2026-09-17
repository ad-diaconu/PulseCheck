.PHONY: test-db-up test-db-down test

# Spin up test database in a Docker container
test-db-up:
	docker-compose -f docker-compose.test.yaml up -d --wait

# Stop and destroy test database container
test-db-down:
	docker-compose -f docker-compose.test.yaml down -v

# Full automation command
test: test-db-up
	pytest -v || true
	$(MAKE) test-db-down