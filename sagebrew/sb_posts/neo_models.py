import pytz

from datetime import datetime

from neomodel import (StructuredNode, StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty, FloatProperty, ZeroOrOne)


class PostedOnRel(StructuredRel):
    shared_on = DateTimeProperty(default=lambda: datetime.now(pytz.utc))

class PostReceivedRel(StructuredRel):
    received = BooleanProperty()


class SBPost(StructuredNode):
    content = StringProperty()
    post_id = StringProperty(unique_index=True)

    #relationships
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'OWNED_BY', model=PostedOnRel)
    up_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'UP_VOTED_BY')
    down_voted_by = RelationshipTo('plebs.neo_models.Pleb', 'DOWN_VOTED_BY')
    flagged_by = RelationshipTo('plebs.neo_models.Pleb', 'FLAGGED_BY')
    received_by = RelationshipTo('plebs.neo_models.Pleb', 'RECEIVED', model=PostReceivedRel)
    comments = RelationshipTo('sb_comments.neo_models.SBComment', 'HAS_A', model=PostedOnRel)
    #TODO Implement referenced_by_... relationships
    #TODO Implement ..._referenced relationships