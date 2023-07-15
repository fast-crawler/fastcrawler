#! /bin/bash

tox -e format
tox -e pytest
tox -e typecheck
tox -e lint
