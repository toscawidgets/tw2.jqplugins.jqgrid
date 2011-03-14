import tw2.core
import tw2.core.util
from tw2.core.resources import encoder

import sqlalchemy as sa
import sqlalchemy.orm.properties

from tw2.jqplugins.jqgrid.widgets.core import jqGridWidget

import math

    
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
    def _make_model(cls, prop):
        return {
            'name': prop.key,
            'label': tw2.core.util.name2label(prop.key),
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
        props = cls._get_properties()
        return [getattr(entry, p.key) for p in props]

    def prepare(self):
        if not getattr(self, 'entity', None):
            raise ValueError, "SQLAjqGridWidget must be supplied an 'entity'"

        if not getattr(self, 'options', None):
            raise ValueError, "SQLAjqGridWidget must be supplied a 'options'"

        if 'url' not in self.options:
            raise ValueError, "SQLAjqGridWidget options must contain 'url'"

        
        _options = self.options
        super(SQLAjqGridWidget, self).prepare() 

        _options.update({
            'pager': "%s_pager" % self.id,
            'caption': tw2.core.util.name2label(self.entity.__name__),
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
        kw = {
            'page' : 1,        'rows' : 10000,
            'sord' : 'desc',   'sidx' : 'created_on',
            '_search' : '',     'nd' : 0,
        }
        kw.update(req.params)

        # Cast things to integers
        kw['page'], kw['rows'] = map(int, [kw['page'], kw['rows']])

        pkey = sa.orm.class_mapper(cls.entity).primary_key[0].key

        base = cls.entity.query
        entries = base.offset((kw['page']-1)*kw['rows']).limit(kw['rows']).all()
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
 


