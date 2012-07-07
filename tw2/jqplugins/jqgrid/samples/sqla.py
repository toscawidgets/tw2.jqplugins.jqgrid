"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""
from tw2.jqplugins.jqgrid.widgets import SQLAjqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css

from tw2.jqplugins.jqgrid.samples import model


class DemoSQLAJQGridWidget(SQLAjqGridWidget):

    def prepare(self):
        self.resources.append(word_wrap_css)
        super(DemoSQLAJQGridWidget, self).prepare()

    entity = model.Person

    excluded_columns = ['id', 'job_id']

    options = {
        'url': '/db_jqgrid/',
        'editurl': '/db_jqgrid/',
        'rowNum': 15,
        'rowList': [15, 30, 50],
        'viewrecords': True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 590,
        'height': 'auto',

        'pager': 'module-1-demo_pager',
    }

    prmFilter = {'stringResult': True, 'searchOnEnter': False}

    pager_options = {
        "search": False,
        "refresh": True,
        "add": True,
        "del": False,
    }


import tw2.core as twc
twc.register_controller(DemoSQLAJQGridWidget, 'db_jqgrid')
