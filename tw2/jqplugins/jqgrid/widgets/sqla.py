import tw2.core
import tw2.core.util
from tw2.core.resources import encoder
from tw2.core.jsonify import jsonify


import sqlalchemy as sa
from sqlalchemy import or_, and_
import sqlalchemy.types as sat
import sqlalchemy.orm.properties

from tw2.jqplugins.jqgrid.widgets.core import jqGridWidget

import simplejson
import datetime
import math
import transaction

COUNT_PREFIX = '__count_'

def dotted_getattr(obj, field, *args):
    try:
        result = reduce(getattr, field.split('.'), obj)
    except AttributeError, e:
        result = args[0]
    finally:
        return result


def is_attribute(x):
    return type(x) is sqlalchemy.orm.properties.ColumnProperty


def is_relation(x):
    return type(x) is sqlalchemy.orm.properties.RelationshipProperty


class SQLAjqGridWidget(jqGridWidget):
    entity = tw2.core.Param("sqlalchemy class to render", request_local=False)
    excluded_columns = tw2.core.Param(
        """list of names of columns to be excluded. This will only work if
        colModel is not passed.""", default=[])
    datetime_format = tw2.core.Param(
        "format string for formatting datetime objects", default="%x")
    colModel = tw2.core.Param(
            "list,sequence and options of columns to display", default=[])

    show_relations = tw2.core.Param("(bool) show relationships?", default=True)
    show_attributes = tw2.core.Param("(bool) show attributes?", default=True)

    @classmethod
    def exclude_property(cls, p):
        explicitly_excluded = p.key in cls.excluded_columns
        excluded_by_attribute = is_attribute(p) and not cls.show_attributes
        excluded_by_relation = is_relation(p) and not cls.show_relations
        return any([
            explicitly_excluded,
            excluded_by_attribute,
            excluded_by_relation,
        ])

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
        name = prop.key
        if is_relation(prop) and \
           prop.direction.name.endswith('TOMANY') and \
           prop.uselist:
            name = COUNT_PREFIX + prop.key
        return name

    @classmethod
    def _make_model(cls, prop):
        return {
            'name': cls._get_name(prop),
            'align': cls._get_align(prop),
            'label': tw2.core.util.name2label(prop.key),
            'sortable': not (is_relation(prop) and not prop.uselist),
            'editable': not is_relation(prop),
            'search': not is_relation(prop),
            'searchoptions': {'sopt': ['cn']},
        }

    @classmethod
    def _get_properties(cls):
        
        props = []
        if cls.colModel:
            props = [p for p in sa.orm.class_mapper(cls.entity).iterate_properties]
            new_props = []
            for col in cls.colModel:
                for p in props:
                    if p.key == col['name']:
                        new_props.append(p)
            props = new_props

        else:
            props = [p for p in
                    sa.orm.class_mapper(cls.entity).iterate_properties if not
                    cls.exclude_property(p)]
            # Reorder properties to put relationships last
            def relation_sorter(x, y):
                xname = dotted_getattr(x, 'direction.name', 'a')
                yname = dotted_getattr(y, 'direction.name', 'a')
                return -1 * cmp(xname, yname)
            props.sort(relation_sorter)

        return props

    @classmethod
    def _get_metadata(cls):
        props = cls._get_properties()
        colmodel = [cls._make_model(p) for p in props] \
                if not cls.colModel else cls.colModel
        return {
            'colNames': [e.get('label', "No Label Set") for e in colmodel],
            'colModel': colmodel
        }

    @classmethod
    def _get_data(cls, entry):
        def massage(entry, prop):
            data = getattr(entry, prop.key)
            if hasattr(data, '__unicode__'):
                data = data.__unicode__()
            elif is_relation(prop) and prop.direction.name.endswith('TOMANY'):
                if prop.uselist:
                    data = len(data)
                else:
                    data = unicode(data)
            elif is_relation(prop) and not prop.uselist:
                data = unicode(data)

            if isinstance(data, datetime.datetime):
                data = data.strftime(cls.datetime_format)

            return data
        return [massage(entry, prop) for prop in cls._get_properties()]

    @classmethod
    def _get_subquery_lookup(cls):
        subquery_lookup = {}
        # TODO -- the *meaning* of local and remote are used
        # incorrectly everywhere :)
        for prop in cls._get_properties():
            if (is_relation(prop)
                and prop.direction.name.endswith('TOMANY')
                and not prop.uselist):
                continue  # One to One relation.  We do nothing.
            elif is_relation(prop) and prop.direction.name == 'MANYTOMANY':
                ent = {
                    'cls': prop.secondary,
                    'local': 'c.' + prop.remote_side[0].key,
                    'remote': prop.local_side[0].key,
                }
            elif is_relation(prop) and prop.direction.name == 'ONETOMANY':
                ent = {
                    'cls': prop.mapper._identity_class,
                    'local': prop.remote_side[0].key,
                    'remote': prop.local_side[0].key,
                }
            elif is_relation(prop) and prop.direction.name == 'MANYTOONE':
                continue  # TODO
            else:
                continue
                # TODO -- other types of relations

            subquery_lookup[COUNT_PREFIX + prop.key] = ent
        return subquery_lookup

    @classmethod
    def _query_filter(cls, oper, col, string):
        if oper == 'eq':
            return col == string
        elif oper == 'ne':
            return col != string
        elif  oper == 'lt':
            return col < string
        elif oper == 'le':
            return col <= string
        elif oper == 'gt':
            return col > string
        elif oper == 'ge':
            return col >= string
        elif oper == 'bw':
            return col.ilike(string + '%')
        elif oper == 'ew':
            return col.ilike('%' + string)
        elif oper == 'cn':
            return col.ilike('%' + string + '%')

    @classmethod
    def _searched_query(cls, query, kw):
        if 'filters' in kw:
            filters = simplejson.loads(kw['filters'])
            if filters['groupOp'] == 'AND':
                and_query = []
                for rule in filters['rules']:
                    col = getattr(cls.entity, rule['field'])
                    and_query.append(
                        cls._query_filter(rule['op'], col, rule['data']))
                query = query.filter(and_(*and_query))
            elif filters['groupOp'] == 'OR':
                or_query = []
                for rule in filters['rules']:
                    col = getattr(cls.entity, rule['field'])
                    or_query.append(
                        cls._query_filter(rule['op'], col, rule['data']))
                query = query.filter(or_(*or_query))
        return query

    @classmethod
    def _build_sorted_query(cls, kw):
        # A little lookup table for sorting
        orders = {'desc': sqlalchemy.desc, 'asc': sqlalchemy.asc, }

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

            # TODO -- remove this?  Currently unused vestigial organ.
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

        query = query.order_by(orders[kw['sord']](sort_on))
        return query

    @classmethod
    def _collapse_subqueries(cls, entries):
        _entries = []
        properties = cls._get_properties()
        for entry in entries:
            if not hasattr(entry, cls.entity.__name__):
                _entries.append(entry)
                continue

            obj = getattr(entry, cls.entity.__name__)
            for prop in properties:
                if prop.key.startswith(COUNT_PREFIX):
                    setattr(obj, getattr(entry, COUNT_PREFIX + prop.key))

            _entries.append(obj)

        return _entries

    def prepare(self):
        if not getattr(self, 'entity', None):
            raise ValueError("SQLAjqGridWidget must be supplied an 'entity'")

        if not getattr(self, 'options', None):
            raise ValueError("SQLAjqGridWidget must be supplied an 'options'")

        if 'url' not in self.options:
            raise ValueError("SQLAjqGridWidget options must contain 'url'")

        _options = self.options
        super(SQLAjqGridWidget, self).prepare()

        pkey = sa.orm.class_mapper(self.entity).primary_key[0].key
        
        # Derive caption from table name if not passed as argument
        if not _options['caption']:
            _options.update({
                'caption': tw2.core.util.name2label(self.entity.__name__)
            })

        _options.update({
            'sortname': pkey,
            'datatype': 'json',
        })

        _options.update(type(self)._get_metadata())
        self.options = encoder.encode(_options)

    @classmethod
    @jsonify
    def request(cls, req):
        if req.GET:
            return cls._request_query(req)
        elif req.POST:
            return cls._request_post(req)
        else:
            print "Neither a GET nor a POST..  dunno what do to."
            raise ValueError("Failboat.")

    @classmethod
    def _massage_post_params(cls, params):
        kwargs = dict(params)

        # Prune empty values
        for key, value in kwargs.items():
            if not value:
                kwargs.pop(key)

        # Do some data massaging (strings -> datetime objects)
        for prop in filter(is_attribute, cls._get_properties()):
            if prop.key not in kwargs:
                continue
            if type(prop.columns[0].type) == sqlalchemy.types.DateTime:
                kwargs[prop.key] = datetime.datetime.strptime(
                    kwargs[prop.key],
                    cls.datetime_format
                )

        return kwargs

    @classmethod
    def _request_post_add(cls, req):
        kwargs = cls._massage_post_params(req.params)

        del kwargs['oper']
        del kwargs['id']
        obj = cls.entity(**kwargs)
        obj.query.session.add(obj)
        transaction.commit()
        return {}

    @classmethod
    def _request_post_edit(cls, req):
        kwargs = cls._massage_post_params(req.params)

        obj = cls.entity.query.filter_by(id=kwargs['id']).one()

        del kwargs['oper']
        del kwargs['id']

        for key, value in kwargs.items():
            setattr(obj, key, value)

        transaction.commit()
        return {}

    @classmethod
    def _request_post(cls, req):
        if not 'oper' in req.params:
            raise ValueError("No operation specified.")

        method_name = "_request_post_%s" % req.params['oper']
        return getattr(cls, method_name)(req)

    @classmethod
    def _request_query(cls, req):
        try:
            pkey = sa.orm.class_mapper(cls.entity).primary_key[0].key
            kw = {
                'page': 1,
                'rows': 10000,
                'sord': 'desc',
                'sidx': pkey,
                '_search': 'False',
                'nd': 0,
            }
            kw.update(req.params)

            # Cast things to integers
            kw['page'], kw['rows'] = map(int, [kw['page'], kw['rows']])

            base = cls._build_sorted_query(kw)

            if kw['_search'] and kw['_search'].lower() == 'true':
                base = cls._searched_query(base, kw)

            entries = base.offset(
                (kw['page'] - 1) * kw['rows']
            ).limit(kw['rows']).all()
            entries = cls._collapse_subqueries(entries)
            count = base.count()

            return {
                "page": kw['page'],
                "total": int(math.ceil(float(count) / kw['rows'])),
                "records": count,
                "rows": [
                    {
                        "id": getattr(entry, pkey),
                        "cell": cls._get_data(entry)
                    } for entry in entries]
            }
        except Exception, e:
            import traceback
            traceback.print_exc(e)
            raise
