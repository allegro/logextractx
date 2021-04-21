PYTEST=pytest $(PYTEST_PARAMS)
COV_PARAMS=--cov=logextractx --cov-report=html --cov-report=term-missing --no-cov-on-fail \
            --cov-fail-under=100 --cov-branch
PYTEST_PARAMS=--tb=native -v --color=auto $(COV_PARAMS)

export TWINE_USERNAME?=__token__
export TWINE_PASSWORD?=your_token

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

build: clean
	pip3 install --upgrade build
	python3 -m build

publish:
	make build
	pip3 install --upgrade twine
	twine upload --verbose dist/*

clean:
	rm -rf dist build
