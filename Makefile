.PHONY: create-venv
create-venv:
	@pipenv install

.PHONY: venv
venv:
	@pipenv shell

.PHONY: bump-patch
bump-patch:
	@bump2version patch
	@git push --tags
	@git push

.PHONY: bump-minor
bump-minor:
	@bump2version minor
	@git push --tags
	@git push

.PHONY: bump-major
bump-major:
	@bump2version major
	@git push --tags
	@git push

.PHONY: release_patch
release_patch:
	@./release_step.sh patch
	@git push --follow-tags