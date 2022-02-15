.PHONY: create-venv
create-venv:
	@pipenv install

.PHONY: venv
venv:
	@pipenv shell

.PHONY: bump-patch
bump-patch:
	@bump2version patch

.PHONY: bump-minor
bump-minor:
	@bump2version minor

.PHONY: bump-major
bump-major:
	@bump2version major