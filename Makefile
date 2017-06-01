PIP := .env/bin/pip
TOX := .env/bin/tox
PYTHON := .env/bin/python

# create virtual environment
.env:
	virtualenv .env -p python3

# install all needed for development
develop: .env
	$(PIP) install -r requirements-dev.txt -r requirements-test.txt -e .

test: .env
	$(PIP) install tox
	$(TOX)

pypi:
	$(PYTHON) setup.py sdist upload

# clean the development envrironment
clean:
	-rm -rf .env .tox
