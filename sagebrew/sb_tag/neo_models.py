from uuid import uuid1

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo, StructuredRel, BooleanProperty,
                      FloatProperty)

from api.neo_models import SBObject


class TagRelevanceModel(StructuredRel):
    relevance = FloatProperty(default=0)


class FrequentTagModel(StructuredRel):
    count = IntegerProperty(default=1)
    in_sphere = BooleanProperty(default=False)


class Tag(SBObject):
    object_uuid = StringProperty(default=uuid1, index=True)
    name = StringProperty(unique_index=True)
    tag_used = IntegerProperty(default=0)
    base = BooleanProperty(default=False)
    
    # relationships
    frequently_tagged_with = RelationshipTo('sb_tag.neo_models.Tag',
                                            'FREQUENTLY_TAGGED_WITH',
                                            model=FrequentTagModel)


class AutoTag(Tag):
    generated_from = StringProperty(default='alchemyapi')

