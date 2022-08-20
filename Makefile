#  -*- mode: makefile; -*-
# Inspired by https://tech.davis-hansson.com/p/make/

SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules
MAKEFLAGS += --no-print-directory

# Note MacOS ships with BSD Make 3.81, so need to install GNU Make 4.x via homebrew (brew install make)
# and place the gnubin on $PATH.
# We could probably get away with not using RECIPEPREFIX, but will do so for now since internal
# Equium standard
ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >

POETRY := poetry


poetry.lock: pyproject.toml
# If it is a new package, help by generating a lock file,
# but otherwise don't re-run poetry lock automatically as it will upgrade
# packages
> test -f  poetry.lock || $(POETRY) lock
# In case poetry.lock existed before pyproject.toml, update the target
> touch -c poetry.lock

.venv: poetry.lock poetry.toml
> $(POETRY) install $(POETRY_INSTALL_OPTIONS)
# In case .venv existed before poetry.lock, update the target
> touch -c .venv


init: .venv
.PHONY: init


clean:
> rm -rf .venv *.egg-info pip-wheel-metadata .mypy_cache .coverage build dist
> find . -name "*.pyc" -type f -delete
> find . -type d -empty -delete
.PHONY: init


CHECK_ONLY ?=
ifdef CHECK_ONLY
ISORT_ARGS=--check-only -q
BLACK_ARGS=--check -q
else
ISORT_ARGS=
BLACK_ARGS=
endif
format:
> $(POETRY) run isort --virtual-env .venv $(ISORT_ARGS) .
> $(POETRY) run black $(BLACK_ARGS) .
.PHONY: format


lint:
> $(POETRY) run flake8 .
> CHECK_ONLY=true $(MAKE) format
# FIXME add mypy to lint (few failures make GH Actions)
# > $(MAKE) mypy
.PHONY: lint


mypy:
> $(POETRY) run mypy --namespace-packages -p mazel
.PHONY: mypy


test:
> $(POETRY) run python -m unittest discover -t . -s tests
.PHONY: init



build:
> $(POETRY) build
.PHONY: build


publish: build
> $(POETRY) publish
.PHONY: publish
