import transaction
from sqlalchemy import (
    Column, Integer, Unicode, DateTime,
    MetaData, Table, ForeignKey,
)
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

import tw2.sqla as tws
    
import random
from random import randint
from datetime import datetime, timedelta

session = tws.transactional_session()
Base = declarative_base(metadata=MetaData('sqlite:///%s.db' % __name__))
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
    birf_day = Column(
        DateTime, nullable=False,
        default=lambda:datetime.now()-timedelta(randint(0, 2000)))

    # One-to-one
    pet = relation('Pet', backref='owner', uselist=False)
    # One-to-many
    children = relation('Child', backref='parent')
    # Many-to-one
    job_id = Column(Integer, ForeignKey('jobs.id'))

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

class Pet(Base):
    __tablename__ = 'pets'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    variety = Column(Unicode(255), nullable=False)
    owner_id = Column(Integer, ForeignKey('persons.id'))

    def __unicode__(self):
        return self.name

class Child(Base):
    __tablename__ = 'children'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    parent_id = Column(Integer, ForeignKey('persons.id'))

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), nullable=False)
    persons = relation('Person', backref='job')

    def __unicode__(self):
        return self.name



Person.__mapper__.add_property('friends', relation(Person,
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

    job_names = ["Programmer", "Sysadmin", "Suit"]
    jobs = [Job(name=job_name) for job_name in job_names]
    [sess.add(job) for job in jobs]

    pet_names = ["Spot", "Mack", "Cracker", "Fluffy", "Alabaster",
                 "Slim Pickins", "Lil' bit", "Balthazaar", "Hadoop"]
    varieties = ["dog", "cat", "bird", "fish", "hermit crab", "lizard"]

    for person in Person.query.all():
        pet = Pet(name=pet_names[random.randint(0,len(pet_names)-1)],
                  variety=varieties[random.randint(0,len(varieties)-1)])
        sess.add(pet)
        person.pet = pet
        for i in range(0, random.randint(0, 4)):
            child = Child(name=firsts[random.randint(0, len(firsts)-1)])
            sess.add(child)
            person.children.append(child)
            person.job = jobs[random.randint(0, len(jobs)-1)]


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
