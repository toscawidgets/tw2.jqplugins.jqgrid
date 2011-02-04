
import tw2.jquery.base as twjq_c
import defaults

jqgrid_css = twjq_c.jQueryPluginCSSLink(
    name=defaults._jqgrid_name_,
    version = defaults._jqgrid_version_,
    basename = defaults._jqgrid_css_basename_,
    modname = 'tw2.jqplugins.jqgrid',
)
word_wrap_css = twjq_c.jQueryPluginCSSLink(
    name=defaults._jqgrid_name_,
    version = defaults._jqgrid_version_,
    basename = defaults._jqgrid_css_basename_,
    modname = 'tw2.jqplugins.jqgrid',
    variant='word_wrap',
)

jqgrid_locale = twjq_c.jQueryPluginJSLink(
    name=defaults._jqgrid_name_,
    basename='grid.locale-%s' % defaults._jqgrid_locale_,
    subdir='js/i18n',
    version=defaults._jqgrid_version_,
    modname='tw2.jqplugins.jqgrid',
)

jqgrid_js = twjq_c.jQueryPluginJSLink(
    name=defaults._jqgrid_name_,
    version=defaults._jqgrid_version_,
    variant='min',
    modname='tw2.jqplugins.jqgrid',
)

__all__ = ['jqgrid_js', 'jqgrid_locale', 'jqgrid_css']
