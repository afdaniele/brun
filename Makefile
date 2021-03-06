ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PART=patch

all:

new-dist:
	$(MAKE) clean bump-upload

bump-upload:
	$(MAKE) test bump upload

bump:
	bumpversion ${PART}

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

format:
	yapf -r -i -p -vv ${ROOT_DIR}

test:
	$(MAKE) test-unit
	$(MAKE) -f ${ROOT_DIR}/tests/distribution/Makefile test-all

test-unit:
	$(MAKE) test-one-unit TEST="test_*"

test-one-unit:
	@echo "Running unit tests:"; echo ""
	@PYTHONPATH="${ROOT_DIR}:$${PYTHONPATH}" \
		python3 \
			-m unittest discover \
			--verbose \
			-s "${ROOT_DIR}/tests/unit" \
			-p "${TEST}.py"
