# create virtual environment
.env:
	virtualenv .env -p python3

# install all needed for development
develop: .env
	.env/bin/pip install -r requirements.txt -e . tox

test: develop
	python setup.py test

# clean the development envrironment
clean:
	-rm -rf .env
