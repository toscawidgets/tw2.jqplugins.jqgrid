


from tw2.core.resources import encoder
import tw2.core as twc

import tw2.jquery.core
import tw2.jquery.core.base as tw2_jq_c_b

import formencode.validators as fv
import base

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


class jqGridWidget(tw2.jquery.core.JQueryWidget):
    resources = [base.jqgrid]
    template = "tw2.jquery.jqgrid.templates.jqgrid"
    
    options = twc.Param("Configuration options to pass to jqgrid", default={})
    pager_options = twc.Param("Configuration options for pager", default={})

    def prepare(self):
        super(jqGridWidget, self).prepare()
        if not self.options:
            raise ValueError, 'jqGridWidget must be supplied a dict of options'

        
        if (
            not 'url' in self.options and
            not 'data' in self.options and
            not 'datastr' in self.options):
            raise ValueError, "jqGridWidget must be supplied a " + \
                              "'url', 'data', or 'datastr' in options"

        self._options = encoder.encode(self.options)
        self._pager_options = encoder.encode(self.pager_options)
