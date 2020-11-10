build:
	python3 setup.py build --verbose

install:
	python3 setup.py install --verbose --user

uninstall:
	pip uninstall --verbose --yes fce-ipmi
	rm --verbose ~/.local/bin/fce-ipmi

freeze:
	pip freeze | grep -v 'fce-ipmi' > requirements.txt

clean:
	python3 setup.py clean
	find . -name '*.pyc' -exec rm --verbose --force {} +
	find . -name __pycache__ -type d -exec rm --verbose --recursive --force {} +
	find . -name '*.egg-info' -type d -exec rm --verbose --recursive --force {} +
	rm --verbose --recursive --force build/
	rm --verbose --recursive --force dist
	rm --verbose --recursive --force .eggs
