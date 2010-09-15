from base import jQueryJSLink, jQueryCSSLink, jQueryPluginJSLink, jQueryPluginCSSLink, jQueryUIThemeCSSLink, jQueryUIJSLink
from tw2.core.resources import encoder
import formencode.validators as fv
import defaults

jquery_js = jQueryJSLink()

####
####
#### JQuery plugins
####
####

# SwitchView
jswitchview_js = jQueryPluginJSLink(name=defaults._switchview_name_, version=defaults._switchview_version_)
jswitchview_css = jQueryPluginCSSLink(name=defaults._switchview_name_, version=defaults._switchview_version_)
jswitchview = jQueryJSLink(resources=[jswitchview_js, jswitchview_css])

#Jcrop
jcrop_css = jQueryPluginCSSLink(name=defaults._jcrop_name_, version=defaults._jcrop_version_)
jcrop_js = jQueryPluginJSLink(name=defaults._jcrop_name_, version=defaults._jcrop_version_)

# The usable piece, I couldn't figure out a better way to do dependencies
jcrop = jQueryJSLink(resources = [jcrop_js, jcrop_css])

#jquery.ui
# Note we use the default smoothness theme
jquery_ui_css = jQueryUIThemeCSSLink(name=defaults._ui_theme_name_, version=defaults._ui_version_)
jquery_ui_js = jQueryUIJSLink(version=defaults._ui_version_)

jquery_ui = jQueryJSLink(resources = [jquery_ui_css, jquery_ui_js])

#jqgrid
jqgrid_css = jQueryPluginCSSLink(name=defaults._jqgrid_name_, version = defaults._jqgrid_version_, basename = defaults._jqgrid_css_basename_)
jqgrid_locale = jQueryPluginJSLink(name=defaults._jqgrid_name_, basename='grid.locale-%s' % defaults._jqgrid_locale_, subdir='js/i18n', version=defaults._jqgrid_version_)
jqgrid_js = jQueryPluginJSLink(name=defaults._jqgrid_name_, version = defaults._jqgrid_version_, variant='min')

jqgrid = jQueryJSLink(resources = [jquery_ui_css, jquery_ui_js, jqgrid_locale, jqgrid_js, jqgrid_css])

####
####
#### Jquery enabled widgets
####
####

jnullable_js = jQueryPluginJSLink(name=defaults._nullable_name_, version=defaults._nullable_version_)

import tw2.forms.widgets
import tw2.core as twc

class NullableSelectionField(tw2.forms.widgets.SelectionField):
    input_class = 'nullable'
    title_text = twc.Param("Text to use as the tool tip for each radio button", default="Select an option, or click a selected option to deselect it.")
    resources = [jquery_js, jnullable_js]

    def prepare(self):
        super(NullableSelectionField, self).prepare()
        #Add the input_class value to the class list
        for opt in self.options:
            opt[0]['class'] = self.input_class
            opt[0]['title'] = self.title_text

class NullableRadioButtonList(NullableSelectionField, tw2.forms.widgets.RadioButtonList): pass

class NullableRadioButtonTable(NullableSelectionField, tw2.forms.widgets.RadioButtonTable):
    """TODO: Fix the prepare path"""
    pass

_pager_defaults = {'enableSearch': True, 'enableClear': True, 'gridModel': True}

import formencode as fe
import formencode.validators as fv
class jqGridFilterSchema(fe.Schema):
    allow_extra_fields=True

    page = fv.Int(if_empty=1, not_empty=False, if_missing=1)
    rows = fv.Int(if_empty=10, not_empty=False, if_missing=1)
    sidx = fv.String(if_empty=None, not_empty=False, if_missing=None)
    sord = fv.String(if_empty=None, not_empty=False, if_missing=None)
    _search = fv.StringBool(if_empty=False, not_empty=False, if_missing=False)
    searchField = fv.String(if_empty=None, not_empty=False, if_missing=None)
    searchString = fv.String(if_empty=None, not_empty=False, if_missing=None)
    searchOper = fv.String(if_empty=None, not_empty=False, if_missing=None)


class jqGrid(twc.Widget):
    resources = [jqgrid]
    url = twc.Param("Url that jqGrid should pull its data from", default=None)
    options = twc.Param("Extra options to pass to jqgrid: Defaults {}", default = {})
    pager_options = twc.Param("Extra options to pass to jqgrid's pager: Defaults %s" % str(_pager_defaults), default = _pager_defaults)
    paginate = twc.Param("Will the widget show the pager?", default=None)
    template = "tw2.jquery.core.templates.jqgrid"

    def prepare(self):
        super(jqGrid, self).prepare()
        self._url = encoder.encode(self.url)
        self._options = encoder.encode(self.options)
        self._pager_options = {}
        for k, v in self.pager_options.iteritems():
            self._pager_options[k] = encoder.encode(v)
        if self.paginate:
            self._pager = 'pag_' + self.attrs['id']
        else:
            self._pager = None
        self._pager = encoder.encode(self._pager)
