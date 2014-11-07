from uuid import uuid1

from neomodel import (StructuredNode, BooleanProperty, StringProperty,
                      RelationshipTo, IntegerProperty)


class SBVote(StructuredNode):
    vote_id = StringProperty(unique_index=True, default=lambda: str(uuid1()))
    reputation_adjustment = IntegerProperty()
    vote_type = BooleanProperty() # True is up and False is down

    #relationships
    from_pleb = RelationshipTo('plebs.neo_models.Pleb', 'MADE_VOTE')
    vote_on = RelationshipTo('sb_posts.neo_models.SBContent', 'VOTE_ON')
