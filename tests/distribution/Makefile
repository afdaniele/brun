ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

test:
	docker build \
		--file ${ROOT_DIR}/Dockerfile \
		--build-arg PYTHON_VERSION=${PYTHON_VERSION} \
		--tag afdaniele/brun:test-${PYTHON_VERSION} \
		${ROOT_DIR}/../../ \
	&& docker rmi afdaniele/brun:test-${PYTHON_VERSION}

test-all:
	set -e; \
	while read p; do \
	  make --file ${ROOT_DIR}/Makefile test PYTHON_VERSION=$${p}; \
	done <${ROOT_DIR}/python-versions.txt
