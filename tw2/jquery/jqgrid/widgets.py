


from tw2.core.resources import encoder
import tw2.core as twc

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


class jqGrid(twc.Widget):
    resources = [base.jqgrid]
    url = twc.Param("Url that jqGrid should pull its data from", default=None)
    options = twc.Param("Extra options to pass to jqgrid", default={})
    pager_options = twc.Param(
        "Extra options to pass to jqgrid's pager", default=_pager_defaults)
    paginate = twc.Param("Will the widget show the pager?", default=None)
    template = "tw2.jquery.jqgrid.templates.jqgrid"

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
