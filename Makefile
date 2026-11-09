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

RESUME_DIR := tools/resume
# Point this at a generated YAML (e.g. a tag-filtered variant) to build something other than the default resume.
# It must live in RESUME_DIR so RenderCV picks up the template overrides there.
RESUME_INPUT ?= resume.yaml

.PHONY: resume-build
# Builds the PDF and runs the ATS check. Review rendercv_output/resume.pdf before publishing.
resume-build:
	@cd $(RESUME_DIR) && uv run rendercv render $(RESUME_INPUT) && uv run python check_ats.py rendercv_output/resume.pdf --yaml $(RESUME_INPUT)

.PHONY: resume-publish
# Publishes the already-built PDF as-is (no rebuild): saves it to ~/Documents/resume, backing up
# the old copy, and updates the Google Drive file.
resume-publish:
	@uv run python $(RESUME_DIR)/publish.py
