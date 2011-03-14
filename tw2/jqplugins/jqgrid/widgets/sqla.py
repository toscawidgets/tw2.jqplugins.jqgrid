import tw2.core
import tw2.core.util
from tw2.core.resources import encoder

import sqlalchemy as sa
import sqlalchemy.types as sat
import sqlalchemy.orm.properties

from tw2.jqplugins.jqgrid.widgets.core import jqGridWidget

import math

COUNT_PREFIX = '__count_'

dotted_getattr = lambda obj, field : reduce(getattr, field.split('.'), obj)
    
def is_attribute(x):
    return type(x) is sqlalchemy.orm.properties.ColumnProperty
def is_relation(x):
    return type(x) is sqlalchemy.orm.properties.RelationshipProperty

class SQLAjqGridWidget(jqGridWidget):
    entity = tw2.core.Param("sqlalchemy class to render", request_local=False)
    excluded_columns = tw2.core.Param(
        "list of names of columns to be excluded", default=[])

    show_relations = tw2.core.Param("(bool) show relationships?", default=True)
    show_attributes = tw2.core.Param("(bool) show attributes?", default=True)

    
    @classmethod
    def exclude_property(cls, p):
        explicitly_excluded = p.key in cls.excluded_columns
        excluded_by_attribute = is_attribute(p) and not cls.show_attributes
        excluded_by_relation  = is_relation(p) and not cls.show_relations
        return explicitly_excluded or excluded_by_attribute or excluded_by_relation


    @classmethod
    def _get_align(cls, prop):
        if is_relation(prop) and prop.direction.name.endswith('TOMANY'):
            return 'right'

        for col in getattr(prop, 'columns', []):
            if isinstance(col.type, (sat.Integer, sat.Numeric)):
                return 'right'

        return 'left'

    @classmethod
    def _get_name(cls, prop):
        if is_relation(prop) and prop.direction.name.endswith('TOMANY'):
            return COUNT_PREFIX + prop.key
        return prop.key

    @classmethod
    def _make_model(cls, prop):
        return {
            'name': cls._get_name(prop),
            'align': cls._get_align(prop),
            'label': tw2.core.util.name2label(prop.key),
            'sortable': True,
        }

    @classmethod
    def _get_properties(cls):
        props = [p for p in sa.orm.class_mapper(cls.entity).iterate_properties
                 if not cls.exclude_property(p)]
        return props

    @classmethod
    def _get_metadata(cls):
        props = cls._get_properties()
        colmodel = [cls._make_model(p) for p in props]
        return {
            'colNames' : [e['label'] for e in colmodel],
            'colModel' : colmodel
        }

    @classmethod
    def _get_data(cls, entry):
        def massage(entry, prop):
            data = getattr(entry, prop.key)
            if is_relation(prop) and prop.direction.name.endswith('TOMANY'):
                data = len(data)
            return data
        return [massage(entry, prop) for prop in cls._get_properties()]

    @classmethod
    def _get_subquery_lookup(cls):
        subquery_lookup = {}
        for prop in cls._get_properties():
            if is_relation(prop) and prop.direction.name == 'MANYTOMANY':
                subquery_lookup[COUNT_PREFIX + prop.key] = {
                    'cls' : prop.secondary,
                    'local' : 'c.' + prop.remote_side[0].key,
                    'remote' : prop.local_side[0].key,
                }
            else:
                # TODO -- other types of relations
                pass

        return subquery_lookup


    @classmethod
    def _build_sorted_query(cls, kw):
        # A little lookup table for sorting
        orders = { 'desc' : sqlalchemy.desc, 'asc' : sqlalchemy.asc, }

        # Grab the session from our entity
        session = cls.entity.query.session

        if not kw['sidx'].startswith(COUNT_PREFIX):
            # If we're sorting by normal old attributes, that's nice and easy.
            sort_on = getattr(cls.entity, kw['sidx'])

        subquery_lookup = cls._get_subquery_lookup()
        query_args, subqueries = {}, {}
        for attribute, l in subquery_lookup.iteritems():
            subquery = session.query(
                dotted_getattr(l['cls'], l['local']),
                sqlalchemy.sql.func.count('*').label(attribute)
            ).group_by(dotted_getattr(l['cls'], l['local']))

            if 'subfilter' in l:
                subquery = subquery.filter(l['subfilter'])

            subquery = subquery.subquery()

            query_args[attribute] = getattr(subquery.c, attribute)
            subqueries[attribute] = subquery

        query = session.query(cls.entity, *query_args.values())

        for attribute, l in subquery_lookup.iteritems():
            query = query.outerjoin((
                subqueries[attribute],
                getattr(cls.entity, l['remote']) == \
                getattr(subqueries[attribute].c, l['local'].split('.')[-1])
            ))

            if attribute == kw['sidx']:
                sort_on = getattr(subqueries[attribute].c, kw['sidx'])
            else:
                print attribute, "was not", kw['sidx']

        query = query.order_by(orders[kw['sord']](sort_on))
        return query

    @classmethod
    def _collapse_subqueries(cls, entries):
        properties = cls._get_properties()
        for entry in entries:
            obj = getattr(entry, cls.entity.__name__)
            for prop in properties:
                if prop.key.startswith(COUNT_PREFIX):
                    setattr(obj, getattr(entry, COUNT_PREFIX + prop.key))
            yield obj


    def prepare(self):
        if not getattr(self, 'entity', None):
            raise ValueError, "SQLAjqGridWidget must be supplied an 'entity'"

        if not getattr(self, 'options', None):
            raise ValueError, "SQLAjqGridWidget must be supplied a 'options'"

        if 'url' not in self.options:
            raise ValueError, "SQLAjqGridWidget options must contain 'url'"

        
        _options = self.options
        super(SQLAjqGridWidget, self).prepare() 

        pkey = self.entity.__mapper__.primary_key[0].key
        _options.update({
            'pager': "%s_pager" % self.id,
            'caption': tw2.core.util.name2label(self.entity.__name__),
            'sortname': pkey,
            'datatype': 'json',
        })

        _options.update(type(self)._get_metadata())

        import pprint
        pprint.pprint(_options)

        self.options = encoder.encode(_options)



    from tw2.core.jsonify import jsonify
    @classmethod
    @jsonify
    def request(cls, req):
        pkey = sa.orm.class_mapper(cls.entity).primary_key[0].key
        kw = {
            'page' : 1,        'rows' : 10000,
            'sord' : 'desc',   'sidx' : pkey,
            '_search' : '',     'nd' : 0,
        }
        kw.update(req.params)

        # Cast things to integers
        kw['page'], kw['rows'] = map(int, [kw['page'], kw['rows']])

        base = cls._build_sorted_query(kw)
        entries = base.offset((kw['page']-1)*kw['rows']).limit(kw['rows']).all()
        entries = cls._collapse_subqueries(entries)
        count = base.count()

        return {
            "page" : kw['page'],
            "total" : int(math.ceil(float(count) / kw['rows'])),
            "records" : count,
            "rows" : [
                {
                    "id": getattr(entry, pkey),
                    "cell": cls._get_data(entry)
                } for entry in entries ]
        }
