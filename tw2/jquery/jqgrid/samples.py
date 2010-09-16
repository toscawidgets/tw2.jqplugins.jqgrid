"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""
from widgets import jqGridWidget
class DemojqGridWidget(jqGridWidget):
    # I hope he doesn't mind... :/
    options = {
        'url' : "http://www.trirand.com/blog/jqgrid/demo38/tree.xml",
        'datatype' : 'xml',
        'height' : 'auto',
        'pager' : False,
        'colNames' : ['id', 'Items', 'url'],
        'colModel' : [
            { 
                'name' : 'id',
                'width' : 1,
                'hidden' : True,
                'key' : True
            }, {
                'name' : 'menu',
                'width' : 150,
                'resizable' : False,
                'sortable' : False,
            }, {
                'name' : 'url',
                'width' : 1,
                'hidden' : True
            }
        ],
        'treeGrid' : True,
        'caption' : 'jqGrid Demo',
        'ExpandColumn' : 'menu',
        'autowidth' : True,
        'rowNum' : 200,
    }
