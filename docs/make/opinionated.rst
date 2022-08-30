Opinionated Makefiles
=====================

At Equium we extract out common language-level operations into :file:`//tools/make` that we then ``include`` into smaller Package-level Makefiles

Example Makefile
----------------

Each package's Makefile is mostly just ``include`` statements and setting any variables that need to be overriden.

:file:`//services/backend/Makefile.common`::

   #  -*- mode: makefile; -*-
   include ../../tools/make/Makefile.common
   include ../../tools/make/Makefile.python

   IMAGE_NAME = myproject/backend
   include ../../tools/make/Makefile.docker
   include ../../tools/make/Makefile.mixins-post



:file:`//tools/make/Makefile.common`
------------------------------------

* Common configuration from Davis Hansson's `"Your Makefiles are wrong" <https://tech.davis-hansson.com/p/make/>`_, notably switching to use `>` as the recipe prefix.
* Sets up several variables that are used elsewhere by rules and the targets
* Provides a `make-lazy` function to convert expensive shell computations to only be run when requested

::

   #  -*- mode: makefile; -*-

   SHELL := bash
   .ONESHELL:
   .SHELLFLAGS := -eu -o pipefail -c
   .DELETE_ON_ERROR:
   MAKEFLAGS += --warn-undefined-variables
   MAKEFLAGS += --no-builtin-rules
   MAKEFLAGS += --no-print-directory

   ifeq ($(origin .RECIPEPREFIX), undefined)
   $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
   endif
   .RECIPEPREFIX = >

   SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
   WORKSPACE_DIR := $(abspath $(SELF_DIR)/../../..)
   WORKSPACE_BIN := $(abspath $(WORKSPACE_DIR)/bin)
   PKG_NAME := $(shell basename $(CURDIR))

   GIT_SHA = $(shell git log -1 --format=format:%H)

   MAZEL := $(WORKSPACE_BIN)/mazel

   # TODO Consider a clean-sentinel to rm build/*.sentinel
   clean-sentinels:
   > rm -f build/*.sentinel
   .PHONY: clean-sentinels


   # make a recursive variable lazy (compute once upon usage)
   # Usage:
   #   EXPENSIVE = $(shell run)
   #   $(call make-lazy,EXPENSIVE)
   # From jgc: https://blog.jgc.org/2016/07/lazy-gnu-make-variables.html
   make-lazy = $(eval $1 = $$(eval $1 := $(value $(1)))$$($1))



:file:`//tools/make/Makefile.python`
------------------------------------

::

   #  -*- mode: makefile; -*-

   # Optional Configuration:
   #
   # - BUILD_PREREQS
   #     Extra depedencies for make build
   # - POETRY_EXTRAS
   #     list of packages to be included in `poetry install --extras ...`
   # - TEST_PREREQS
   #     Extra depedencies for make test
   # - SOURCES
   #     .py files that are built into the whl, typically defined via shell find,
   #     defaults to looking in project/ directory


   # Make it easier to adjust which poetry to use during upgrade testing
   POETRY := poetry

   PACKAGE_NAME := $(shell grep "^name" pyproject.toml | cut -f 2 -d '=' | tr -d '" ')
   PACKAGE_VERSION := $(shell grep "^version" pyproject.toml | cut -f 2 -d '=' | tr -d '" ')
   # WARN: assumes the wheel is universal
   PACKAGE_WHL := $(PACKAGE_NAME)-$(PACKAGE_VERSION)-py3-none-any.whl

   TEST_PREREQS ?=

   poetry.lock: pyproject.toml
   # If it is a new package, help by generating a lock file,
   # but otherwise don't re-run poetry lock automatically as it will upgrade
   # packages
   > test -f  poetry.lock || $(POETRY) lock
   # In case poetry.lock existed before pyproject.toml, update the target
   > touch -c poetry.lock

   POETRY_INSTALL_OPTIONS ?=
   ifdef POETRY_EXTRAS
   POETRY_INSTALL_OPTIONS += --extras "$(POETRY_EXTRAS)"
   endif

   # TODO include relative dependencies
   .venv: poetry.lock poetry.toml
   > $(POETRY) install $(POETRY_INSTALL_OPTIONS)
   # In case .venv existed before poetry.lock, update the target
   > touch -c .venv

   INIT_TARGETS += .venv

   ifndef SOURCES
   SOURCES := $(shell find project -name "*.py")
   endif
   BUILD_PREREQS += $(SOURCES)
   BUILD_PREREQS ?=
   BUILD_OUT := dist/$(PACKAGE_WHL)
   $(BUILD_OUT): .venv $(BUILD_PREREQS)
   > $(POETRY) build -f wheel

   build: $(BUILD_OUT)
   .PHONY: build

   TEST_ARGS = -m unittest discover -t . -s tests
   TESTS_EXIST := $(shell test -d tests && echo 1 || echo 0)
   ifeq ($(TESTS_EXIST), 1)
   test-py: .venv $(TEST_PREREQS)
   > $(POETRY) run python $(TEST_ARGS)
   .PHONY: test-py
   TEST_TARGETS += test-py
   endif

   CHECK_ONLY ?=
   ifdef CHECK_ONLY
   ISORT_ARGS=--check-only -q
   BLACK_ARGS=--check -q
   else
   ISORT_ARGS=
   BLACK_ARGS=
   endif
   format:
   # isort will look up parent directories until it finds a .isort.cfg (in workspace root)
   # TODO only format tests/ and `package.name` (extract from pyproject.toml)
   > $(WORKSPACE_BIN)/isort --virtual-env .venv $(ISORT_ARGS) .
   > $(WORKSPACE_BIN)/black $(BLACK_ARGS) .
   .PHONY: format

   lint-py:
   > $(WORKSPACE_BIN)/flake8 .
   > CHECK_ONLY=true $(MAKE) format
   .PHONY: lint-py
   LINT_TARGETS += lint-py

   mypy: .venv
   > $(WORKSPACE_BIN)/mypy \
   >   --config-file=$(WORKSPACE_DIR)/mypy.ini \
   >   --python-executable=.venv/bin/python \
   >   --namespace-packages -p $(PACKAGE_NAME)
   .PHONY: mypy

   _clean_poetry:
   > rm -rf .venv
   .PHONY: _clean_poetry

   _clean_build:
   > rm -rf build dist *.egg-info
   .PHONY: _clean_build

   CLEAN_TARGETS += _clean_poetry _clean_build

   clean-py:
   > rm -rf *.egg-info pip-wheel-metadata .mypy_cache .coverage
   > find . -name "*.pyc" -type f -delete
   > find . -type d -empty -delete
   .PHONY: clean-py
   CLEAN_TARGETS += clean-py clean-sentinels



..

   TODO Makefile.node

:file:`//tools/make/Makefile.docker`
------------------------------------

::

   #  -*- mode: makefile; -*-

   # Required Configuration:
   #
   # - IMAGE_NAME
   #     Name of the docker image (used in tag)
   # - IMAGE_TAG
   #     Image tag. Defaults "latest"
   #
   #
   # Optional Configuration:
   # - IMAGE_BUILD_PATH
   #	  Docker build context root. Default "."
   # - IMAGE_PREREQS
   #     In addition to the Dockerfile, other Makefile prerequisites for image build
   # - GOSS_SLEEP
   #     seconds to wait before running tests, in case process needs to start (default 0.2)
   # - TEST_IMAGE_ARGS
   #     docker arguments to pass into dgoss
   # - TEST_IMAGE_PREREQS
   #     Additional Makefile prerequisites for test-image
   # - TEST_IMAGE_RUN_ARGS
   #     docker run arguments (e.g. after the IMAGE name)

   IMAGE_TAG ?= latest
   IMAGE_BUILD_PATH ?= .
   IMAGE_PREREQS ?=
   GOSS_SLEEP ?= 0.2  # default
   TEST_IMAGE_ARGS ?=
   TEST_IMAGE_PREREQS ?=
   TEST_IMAGE_RUN_ARGS ?=

   image: Dockerfile $(IMAGE_PREREQS)
   > docker build -t $(IMAGE_NAME):$(IMAGE_TAG) \
   >  --build-arg GIT_SHA=$(GIT_SHA) \
   >  -f ${CURDIR}/Dockerfile $(IMAGE_BUILD_PATH)
   .PHONY: image

   # use --platform until we build for arm
   test-image: image $(TEST_IMAGE_PREREQS)
   > GOSS_SLEEP=$(GOSS_SLEEP) GOSS_OPTS="--format rspecish" \
   >  $(WORKSPACE_DIR)/bin/dgoss \
   >  run --platform linux/amd64 $(TEST_IMAGE_ARGS) $(IMAGE_NAME):$(IMAGE_TAG) $(TEST_IMAGE_RUN_ARGS)
   .PHONY: test-image

   clean-image: clean-sentinels
   # TODO implement (sentinel, image?)
   .PHONY: clean-image
   CLEAN_TARGETS += clean-image


.. _opinionated-mixins:

:file:`//tools/make/Makefile.mixins-post`
-----------------------------------------

Since we use :ref:`best-practices-consistent-targets`, we often have one package that needs to run multiple rules for the same target, e.g. `clean` could run `clean-py` and `clean-docker`, our solution is a "mixin" that allows appending targets to a list, that are then all run.

::

   #  -*- mode: makefile; -*-
   # Allows multiple Makefiles.* mixins to contribute to common targets (clean, test, etc),
   # since a concrete Makefile may implement multiple mixins.
   # Since mazel uses `make -n` to dry-run to see if the target exists, we need to wrap
   # the targets in `ifdef`
   #
   # Must be include'ed last and after any added _TARGETS
   #
   # Optional Targets:
   #  - CLEAN_TARGETS: for `make clean`, should use as CLEAN_TARGETS += clean-my-target
   #  - INIT_TARGETS: for `make init`, should use as INIT_TARGETS += init-my-target
   #  - LINT_TARGETS: for `make lint`, should use as LINT_TARGETS += lint-my-target
   #  - TEST_TARGETS: for `make test`, should use as TEST_TARGETS += test-my-target


   ifdef CLEAN_TARGETS
   clean:
   > $(foreach var, $(CLEAN_TARGETS), $(MAKE) $(var);)
   .PHONY: clean
   endif


   ifdef INIT_TARGETS
   init:
   > $(foreach var, $(INIT_TARGETS), $(MAKE) $(var);)
   .PHONY: init
   endif


   ifdef LINT_TARGETS
   lint:
   > $(foreach var, $(LINT_TARGETS), $(MAKE) $(var);)
   .PHONY: lint
   endif


   ifdef TEST_TARGETS
   test:
   > $(foreach var, $(TEST_TARGETS), $(MAKE) $(var);)
   .PHONY: test
   endif
