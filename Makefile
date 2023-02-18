PYTHON := python3.7

help: ## show this help
	@echo "Usage: \033[36mmake <command name> <param name>=<param value> ...\033[0m"
	@echo " "
	@echo "Commands:"
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":"}; {printf "\033[36m  %-15s\033[0m %s\n", $$1, $$2}'

init: ## install required packages
	$(PYTHON) -m pip install -r requirements-dev.txt

checkstyle: ## run static code analyser
	$(PYTHON) -m pylint ./src/* ./tests/* --rcfile=.pylintrc

test: ## run unit tests
	PYTHONPATH="$$PYTHONPATH:./src/" $(PYTHON) -m pytest -v -p no:cacheprovider ./tests/

build: ## build wheel package
	$(PYTHON) -m setup.py bdist_wheel

clean: ## clean workdir
	rm -rf ./.pytest_cache ./build ./dist ./src/*.egg-info

.PHONY: help init checkstyle test build clean
