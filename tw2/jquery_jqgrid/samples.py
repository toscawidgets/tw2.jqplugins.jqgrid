"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""
from widgets import jqGridWidget
from random import random

# No sample b/c its so difficult to find a datasource.

class DemoJQGridWidget(jqGridWidget):
    options = {
        'data': [
            { 'field1' : random(), 'field2' : random() } for i in range(100)
        ],
        'datatype': "local",
        'colNames':['Field1', 'Field2'],
        'colModel':[
            {'name':'field1'},
            {'name':'field2'},
            ],
        'viewrecords': True,
        'rowNum':100,
        'rowList':[100,200],
        'caption':"Example"
}
