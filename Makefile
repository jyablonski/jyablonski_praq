.PHONY: start-postgres
start-postgres:
	@docker compose -f tools/cloud-infra/docker/docker-compose-postgres.yml up -d

.PHONY: stop-postgres
stop-postgres:
	@docker compose -f tools/cloud-infra/docker/docker-compose-postgres.yml down

.PHONY: metabase-up
metabase-up:
	@docker-compose -f tools/data-eng/metabase/docker-compose.yml up -d

.PHONY: metabase-down
metabase-down:
	@docker-compose -f tools/data-eng/metabase/docker-compose.yml down

.PHONY: trino-up
trino-up:
	@docker-compose -f tools/data-eng/trino/docker-compose.yml up -d

.PHONY: trino-down
trino-down:
	@docker-compose -f tools/data-eng/trino/docker-compose.yml down