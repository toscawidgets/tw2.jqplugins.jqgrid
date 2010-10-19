#!/bin/bash

devbase=development-deps
venv=$devbase/virtualenv-tw2.jquery
source $venv/bin/activate

python setup.py install_lib install_egg_info && paster tw2.browser



