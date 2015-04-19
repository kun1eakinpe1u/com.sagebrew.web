from neomodel import (StringProperty, IntegerProperty,
                      DateTimeProperty, RelationshipTo, StructuredRel,
                      BooleanProperty)

from plebs.neo_models import Pleb


class CongressVoteRelationship(StructuredRel):
    pass


class BaseOfficial(Pleb):
    type_str = "f46fbcda-9da8-11e4-9233-080027242395"
    title = StringProperty()
    bio = StringProperty(default="")
    name_mod = StringProperty()
    current = BooleanProperty()
    district = IntegerProperty(default=0)
    state = StringProperty()
    website = StringProperty()
    start_date = DateTimeProperty()
    end_date = DateTimeProperty()
    full_name = StringProperty()
    gov_phone = StringProperty()
    # recipient_id and customer_id are stripe specific attributes
    recipient_id = StringProperty()
    customer_id = StringProperty()
    terms = IntegerProperty()
    twitter = StringProperty()
    youtube = StringProperty()
    # bioguide is used to get the reps public profile picture

    # relationships
    pleb = RelationshipTo('plebs.neo_models.Pleb', 'IS')
    # sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
    #                            "SPONSORED")
    # co_sponsored = RelationshipTo('sb_public_official.neo_models.Bill',
    #                               "COSPONSORED")
    # proposed = RelationshipTo('sb_public_official.neo_models.Bill',
    #                           "PROPOSED")
    # hearings = RelationshipTo('sb_public_official.neo_models.Hearing',
    #                           "ATTENDED")
    # experience = RelationshipTo('sb_public_official.neo_models.Experience',
    #                             "EXPERIENCED")
    goals = RelationshipTo('sb_goals.neo_models.Goal', 'GOAL')
    gt_person = RelationshipTo('govtrack.neo_models.GTPerson', 'GTPERSON')
    gt_role = RelationshipTo('govtrack.neo_models.GTRole', 'GTROLE')

    def get_dict(self):
        crop_name = str(self.full_name).rfind('[')
        try:
            full_name = self.full_name[:crop_name]
        except IndexError:
            full_name = self.full_name
        try:
            bioguideid = self.gt_person.all()[0].bioguideid
        except IndexError:
            bioguideid = None
        return {
            "object_uuid": self.object_uuid,
            "full_name": full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "start_date": unicode(self.start_date),
            "end_date": unicode(self.end_date),
            "state": self.state,
            "title": self.title,
            "district": self.district,
            "current": self.current,
            "bioguide": bioguideid,
            "terms": self.terms,
            "youtube": self.youtube,
            "twitter": self.twitter,
            "channel_wallpaper": None
        }

'''
class Bill(StructuredNode):
    bill_id = StringProperty(unique_index=True)

    # relationships
    proposer = RelationshipTo(BaseOfficial, "PROPOSED_BY")
    sponsor = RelationshipTo(BaseOfficial, "SPONSORED_BY")
    co_sponsor = RelationshipTo(BaseOfficial, "COSPONSORED_BY")


class Hearing(StructuredNode):
    hearing_id = StringProperty(unique_index=True)

    # relationships
    attendees = RelationshipTo(BaseOfficial, "HEARING_ATTENDEES")


class Committee(StructuredNode):
    committee_number = IntegerProperty(unique_index=True)

    # relationships
    members = RelationshipTo(BaseOfficial, "COMMITTEE_MEMBERS")
'''
