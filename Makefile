# create virtual environment
.env:
	virtualenv .env -p python3

# install all needed for development
develop: .env
	.env/bin/pip install -e . tox

# clean the development envrironment
clean:
	-rm -rf .env
