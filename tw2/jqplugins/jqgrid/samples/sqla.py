"""
Here you can create samples of your widgets by providing default parameters,
inserting them in a container widget, mixing them with other widgets, etc...
These samples will appear in the WidgetBrowser

See http://toscawidgets.org/documentation/WidgetBrowser for more information
"""
from tw2.jqplugins.jqgrid.widgets import SQLAjqGridWidget
from tw2.jqplugins.jqgrid.base import word_wrap_css

import transaction
from sqlalchemy import (
    Column, Integer, Unicode,
    MetaData, Table, ForeignKey,
)
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

import tw2.sqla as tws

session = tws.transactional_session()
Base = declarative_base(metadata=MetaData('sqlite:///sample_sqla.db'))
Base.query = session.query_property()

friends_mapping = Table(
    'persons_friends_mapping', Base.metadata,
    Column('friender_id', Integer,
           ForeignKey('persons.id'), primary_key=True),
    Column('friendee_id', Integer,
           ForeignKey('persons.id'), primary_key=True))



class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    first_name = Column(Unicode(255), nullable=False)
    last_name = Column(Unicode(255), nullable=False)
    some_attribute = Column(Unicode(255), nullable=False)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

Person.__mapper__.add_property('friends', relation(
    Person,
    primaryjoin=Person.id==friends_mapping.c.friendee_id,
    secondaryjoin=friends_mapping.c.friender_id==Person.id,
    secondary=friends_mapping,
    doc="List of this persons' friends!",
))

Base.metadata.create_all()

def populateDB(sess):
    if Person.query.count() > 0:
        print "Not populating DB.  Already stuff in there."
        return

    import random

    firsts = ["Sally", "Suzie", "Sandy",
              "John", "Jim", "Joseph"]
    lasts = ["Anderson", "Flanderson", "Johnson",
             "Frompson", "Qaddafi", "Mubarak", "Ben Ali"]

    for first in firsts:
        for last in lasts:
            p = Person(
                first_name=first, last_name=last,
                some_attribute="Fun fact #%i" % random.randint(0,255)
            )
            sess.add(p)

    qaddafis = Person.query.filter_by(last_name='Qaddafi').all()
    mubaraks = Person.query.filter_by(last_name='Mubarak').all()
    benalis = Person.query.filter_by(last_name='Ben Ali').all()
    dictators = qaddafis + mubaraks + benalis

    print "populating dictators friends"
    for p1 in dictators:
        for p2 in dictators:
            if p1 == p2 or p1 in p2.friends:
                continue
            if random.random() > 0.25:
                p1.friends.append(p2)
                p2.friends.append(p1)

    print "populating everyone else's friends"
    for p1 in Person.query.all():
        for p2 in Person.query.all():
            if p1 == p2 or p1 in p2.friends:
                continue
            if random.random() > 0.95:
                p1.friends.append(p2)
                p2.friends.append(p1)

    print "done populating DB"

populateDB(session)
transaction.commit()

class DemoSQLAJQGridWidget(SQLAjqGridWidget):

    def prepare(self):
        self.resources.append(word_wrap_css)
        super(DemoSQLAJQGridWidget, self).prepare()

    entity = Person

    options = {
        'url': '/db_jqgrid/',
        'rowNum':15,
        'rowList':[15,30,50],
        'viewrecords':True,
        'imgpath': 'scripts/jqGrid/themes/green/images',
        'width': 900,
        'height': 'auto',
    }
    pager_options = { "search" : True, "refresh" : True, "add" : False, }


import tw2.core as twc
mw = twc.core.request_local()['middleware']
mw.controllers.register(DemoSQLAJQGridWidget, 'db_jqgrid')
