PYTEST=pytest $(PYTEST_PARAMS)
COV_PARAMS=--cov=logextractx --cov-report=html --cov-report=term-missing --no-cov-on-fail \
            --cov-fail-under=100 --cov-branch
PYTEST_PARAMS=--tb=native -v --color=auto $(COV_PARAMS)

PYPI_REPOSITORY=your-repository
PYPI_PASS=your-pass

TOX_ENVS=""

tests: lints tox

lints:
	flake8 logextractx
	mypy logextractx


tox:
	tox $(TOX_ENVS)

tox-dev:
	tox -e py39-dev


pytest:
	$(PYTEST)

pytestmp:
	$(PYTEST) -m tmp

covreport:
	make tests || open htmlcov/index.html  # probably different command in linux

publish: clean
	python setup.py bdist_wheel
	twine upload -r $(PYPI_REPOSITORY) -p"$(PYPI_PASS)" --verbose dist/*

clean:
	rm -rf dist build
