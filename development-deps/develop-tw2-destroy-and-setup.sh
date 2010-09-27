#!/bin/bash -e

devbase=development-deps
venv=$devbase/virtualenv-tw2.jquery
$(
    rm -rf $venv
) || echo "Did not destroy $venv"

virtualenv $venv --no-site-packages

source $venv/bin/activate

pip install genshi
pip install formencode

pushd $devbase

hg clone http://bitbucket.org/paj/tw2core || \
        (pushd tw2core && hg pull && popd)
hg clone http://bitbucket.org/paj/tw2devtools || \
        (pushd tw2devtools && hg pull && popd)
hg clone http://bitbucket.org/paj/tw2forms || \
        (pushd tw2forms && hg pull && popd)
git clone git://github.com/ralphbean/tw2.jquery_core.git || \
        (pushd tw2.jquery_core && git pull && popd)
git clone git://github.com/ralphbean/tw2.jquery_ui.git || \
        (pushd tw2.jquery_ui && git pull && popd)

pushd tw2core ;  python setup.py develop ; popd
pushd tw2forms ; python setup.py develop ; popd
pushd tw2devtools ; python setup.py develop ; popd
pushd tw2.jquery_core ; python setup.py develop ; popd
pushd tw2.jquery_ui ; python setup.py develop ; popd

pushd # $devbase
