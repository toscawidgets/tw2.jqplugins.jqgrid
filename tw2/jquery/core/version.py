# A simple adapter to quickly replace one version with another, swap debug for production, etc.

# Defaults
_external_          = False

#_variant_           = 'min' # set to '' for debugging
_variant_           = ''

import os
from tw2.core import Link, core
from tw2.core.params import Param
import pkg_resources

class JSLinkError(Exception): pass

# The adapter

class JSLinkMixin(Link):
    name =      Param('(string) The name of the library to link to')
    dirname =   Param('(string) Specify the directory path for the given file, relative to the "static" folder.  Some substitutions are allowed (name and version).')
    basename =  Param('(string) Specify the basename for the given file.')
    version =   Param('(string) Specify the version of the javascript library to use.')
    external =  Param('(boolean) True if you would like to grab the file from a CDN instead of locally.  Default: False', default=_external_)
    url_base =  Param('(string) The base url for fetching the javascript library externally')
    extension = Param('(string) File extension', default = 'js')
    additional_files =  Param('(list(string)) An optional list of files that should be registered with the static resource handler.  Default: []', default=[])

    variant =   Param('File variant, e.g., (min for minified), default is %s' % _variant_, default=_variant_)

#    @property
#    def modname(self):
#        raise NotImplementedError('You must set the modname property on your derived class')

    def __init__(self, *args, **kw):
        self._link = None
        super(Link, self).__init__(*args, **kw)

    def prepare(self):
        if not self.is_external:
            modname = self.modname or self.__module__
            rl = core.request_local()
            resources = rl['middleware'].resources
            resources.register(self.modname, os.path.dirname(self.filename), whole_dir=True)
        super(JSLinkMixin, self).prepare()

    @property
    def core_filename(self):
        ret = self.basename
        if self.variant:
            ret = '.'.join((ret, self.variant))
        ret += '.' + self.extension
        return ret

    @property
    def external_link(self):
        link = '/'.join((self.url_base, self.core_filename))
        return link

    def _get_link(self):
        rl = core.request_local()
        mw = rl['middleware']

        if not self._link:
            if self.external:
                link = self.external_link
            else:
                link = ('/'+'/'.join((mw.config.res_prefix.strip('/'), self.modname, 'static', self.dirname, self.core_filename)) )
            self._link = link
        return self._link % self.substitutions

    def _set_link(self, link):
        self._link = link

    link = property(_get_link, _set_link)#Variable('Direct web link to file. If this is not specified, it is automatically generated, based on :attr:`modname` and :attr:`filename`.', default=property(_get_link, _set_link))

    def abspath(self, filename):
        return os.sep.join((pkg_resources.resource_filename(self.modname, ''),  filename))

    def try_filename(self, filename):
        abspath = self.abspath(filename)
        if os.path.exists(abspath):
            return filename
        raise JSLinkError('File does not exist: %s'%abspath)

    @property
    def substitutions(self):
        return dict(name=self.name, version=self.version)

    @property
    def filename(self):
        #make basename windows/qnix compat
        basename = self.core_filename
        basename = basename.replace('/', os.sep)
        basename = basename.replace('\\', os.sep)

        filename = os.sep.join(('static', self.dirname, basename)) % self.substitutions
        #try the default
        return self.try_filename(filename)

    @property
    def is_external(self):
        return self.external
