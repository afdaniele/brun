all:

bump-upload:
	$(MAKE) bump
	$(MAKE) upload

bump:
	bumpversion patch

upload:
	git push --tags
	git push
	$(MAKE) clean
	$(MAKE) build
	twine upload dist/*

build:
	python3 setup.py sdist

install:
	python3 setup.py install --record files.txt

clean:
	rm -rf dist/ build/ brun.egg-info/ MANIFEST

uninstall:
	xargs rm -rf < files.txt
