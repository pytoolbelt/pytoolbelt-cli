#!/bin/bash

export REQ_FILE = requirements/development.txt
export PROJECT_DIR = pytoolbelt
export TEST_DIR = tests

.PHONY: help
help:                  ## Show help messages and exit.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'


######################### MANAGE PYTHON ENVIRONMENT ####################################

.PHONY: venv
venv:                  ## Create local python venv for development
	if [[ -d ./venv ]]; then rm -rf venv; fi
	python -m venv venv
	. venv/bin/activate pip install --upgrade pip setuptools wheel build


.PHONY: docvenv
docvenv:               ## Create local python venv for documentation
	if [[ -d ./docvenv ]]; then rm -rf docvenv; fi
	python -m venv docvenv && pip install --upgrade pip


.PHONY: install
install:               ## Install project locally in development mode - without dev tools
	. venv/bin/activate && pip install -e .


.PHONY: install-dev
install-dev:           ## Install project locally in development mode - with dev tools
	. venv/bin/activate && pip install -e ".[dev]"


.PHONY: install-docs
install-docs:          ## Install project locally in development mode - with docs tools
	. docvenv/bin/activate && pip install -e ".[docs]"


.PHONY: build-mkdocs
build-mkdocs:          ## Build mkdocs documentation
	. docvenv/bin/activate && mkdocs build


.PHONY: release
release:               ## Install only the dependencies to make a semantic release
	. venv/bin/activate semantic-release publish


######################### RUN TESTS AND LINTER ####################################

.PHONY: format
format:                ## Run black python linter
	. venv/bin/activate && python -m ruff format ${PROJECT_DIR} ${TEST_DIR}

.PHONY: check-format
check-format:          ## Run black linter to check formatting of project files
	. venv/bin/activate && python -m ruff check ${PROJECT_DIR} ${TEST_DIR}

.PHONY: test
test:                  ## Run project tests using pytest
	. venv/bin/activate && python -m pytest ${TEST_DIR} -p no:warnings -s


.PHONY: sort-imports
sort-imports:          ## Sort imports in project files
	. venv/bin/activate && python -m ruff check ${PROJECT_DIR} ${TEST_DIR} --select I --fix


.PHONY: check-sort-imports
check-sort-imports:    ## Run ruff linter to check sorting of imports in project files
	. venv/bin/activate && python -m ruff check ${PROJECT_DIR} ${TEST_DIR} --select I
