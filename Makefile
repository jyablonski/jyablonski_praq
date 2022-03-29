.PHONY: create-venv
create-venv:
	@pipenv install

.PHONY: venv
venv:
	@pipenv shell

.PHONY: bump-patch
bump-patch:
	@./release_step.sh patch
	@git push --follow-tags

.PHONY: bump-minor
bump-minor:
	@./release_step.sh minor
	@git push --follow-tags
.PHONY: bump-major
bump-major:
	@./release_step.sh major
	@git push --follow-tags
