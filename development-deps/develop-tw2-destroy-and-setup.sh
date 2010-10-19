#!/bin/bash -e

devbase=development-deps
venv=$devbase/virtualenv-tw2.jquery
$(
    rm -rf $venv
) || echo "Did not destroy $venv"

virtualenv $venv --no-site-packages

source $venv/bin/activate

pushd $devbase

pip install genshi
pip install mako
pip install formencode

hg clone http://bitbucket.org/paj/tw2core || \
        (pushd tw2core && hg pull && popd)
hg clone http://bitbucket.org/paj/tw2devtools || \
        (pushd tw2devtools && hg pull && popd)
hg clone http://bitbucket.org/paj/tw2forms || \
        (pushd tw2forms && hg pull && popd)
hg clone http://bitbucket.org/toscawidgets/tw2jquery || \
        (pushd tw2jquery && hg pull && popd)
git clone http://github.com/ralphbean/tw2.jquery.plugins.ui.git || \
        (pushd tw2.jquery.plugins.ui && git pull && popd)
#hg clone https://ralphbean@bitbucket.org/toscawidgets/tw2jquery || \
#        (pushd tw2jquery && hg pull && popd)

pushd tw2core ;  python setup.py install ; popd
pushd tw2forms ; python setup.py install ; popd
pushd tw2devtools ; python setup.py install ; popd
pushd tw2jquery ; python setup.py install_lib install_egg_info ; popd
pushd tw2.jquery.plugins.ui ; python setup.py install_lib install_egg_info ; popd

popd # $devbase
