.PHONY: all
all: virtual lint

.PHONY: virtual
virtual: requirements.txt
	python3 -m pip install virtualenv; \
	python3 -m virtualenv venv; \
	. venv/bin/activate; \
	pip install -r requirements.txt

.PHONY: lint
lint: test_module/*.py test/tests.py
	\
 	. venv/bin/activate; \
	pip -V; \
	isort test_module/*.py test/tests.py; \
	black --line-length 120 test_module/*.py test/tests.py; \
	bandit -v test_module/*.py --skip=B301,B403; \

.PHONY: clean
clean:
	rm -rf venv
