#!/bin/bash

venv=virtualenv-tw2.jquery.jqgrid
source $venv/bin/activate

python setup.py develop && paster tw2.browser



