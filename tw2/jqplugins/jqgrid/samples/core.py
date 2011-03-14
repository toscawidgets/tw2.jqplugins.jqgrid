"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""
from tw2.jqplugins.jqgrid.widgets import jqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css
from random import random
from random import randint
r = lambda x : randint(0,x-1)

# No sample b/c its so difficult to find a datasource.

def generate_data(n):
    fnames = ['S.', 'J.']
    lnames = ['Flanderson', 'Anderson', 'Sanderson', 'Boot', 'Bean', 'Resig']
    intros = ['', 'On the', 'Regarding the', 'On', 'New Developments in',
              'A Survey of the',
             ]
    adjectives = ['Scientific', 'Schmientific', 'Cosmological', 'Astronomical',
                  'Computational', 'Fromputational', 'Mechanical', 'Chemical',
                  'Pythonic', 'Functional', 'Declarative', 'Quantum',
                  'Entanglement', 'Singular', 'Non-negative',
                 ]
    nouns = ['Problems', 'Solutions', 'Ins-and-outs', 'Nuances',
             'Transmogrification', 'Implementation',
            ]
    segues = ['of', 'underlying']
    journals = ['Review', 'Journal', 'Conference']
    for i in range(n):
        authors = ", ".join(["%s %s" % (fnames[r(len(fnames))],
                                        lnames[r(len(lnames))])
                             for j in range(randint(1,2))])
        title = "%s %s %s %s %s %s." %(
            intros[r(len(intros))],
            adjectives[r(len(adjectives))],
            nouns[r(len(nouns))],
            segues[r(len(segues))],
            adjectives[r(len(adjectives))],
            nouns[r(len(nouns))],
        )
        journal = "The %s of %s %s" % (
            journals[r(len(journals))],
            adjectives[r(len(adjectives))],
            nouns[r(len(nouns))],
        )
        published = randint(1955, 2010)
        yield {'authors':authors,
               'title':title,
               'journal':journal,
               'published_on':published}

class DemoJQGridWidget(jqGridWidget):

    def prepare(self):
        self.resources.append(word_wrap_css)
        super(DemoJQGridWidget, self).prepare()

    options = {
        'pager' : 'module-0-demo_pager',
        'caption' : 'All research publications',
        'data' : [row for row in generate_data(55)],
        'datatype' : 'local',
        'colNames':[ 'Authors', 'Title', 'Journal', 'Published' ],
        'colModel' : [
            {
                'name':'authors',
                'width':75,
                'align':'center',
            },{
                'name':'title',
            },{
                'name':'journal',
            },{
                'name':'published_on',
                'width':50,
                'align':'center'
            },
        ],
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 900,
        'height': 'auto',
    }
    pager_options = { "search" : True, "refresh" : True, "add" : False, }
    prmSearch = {
        "sopt": ["cn", "bw"],
        "caption": "Search...",
        "multipleSearch": True,
    }
    custom_pager_buttons = [
        {
            "caption":"",
            "buttonicon":"ui-icon-newwin",
            'onClickButton': None,
            'position': "last",
            'title':"B1",
            'cursor':"pointer"
        },{
            'caption':"",
            'buttonicon':"ui-icon-cart",
            'onClickButton':None,
            'position': "first",
            'title':"B2",
            'cursor': "pointer"
        },
    ]
