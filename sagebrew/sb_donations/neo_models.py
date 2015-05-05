from neomodel import (RelationshipTo, BooleanProperty, IntegerProperty)

from api.neo_models import SBObject


class Donation(SBObject):
    """
    Donations are contributions made from one user to another. Initially this
    will be utilized solely to provide a way to store the donations between
    a user and a user waging a campaign. Eventually we will be utilizing this
    or a derivative of it to also help track donations made to groups, higher
    reputation users, and projects.

    If a user's donation goes over the amount needed for the goal and the
    campaigner is on their first goal or has provided an update on the
    previous goal we release all the funds pledged, we do not attempt to break
    them up. However any donations pledged after that release will result
    in the same process of not being released until the next goal threshold
    is crossed and an update has been provided.
    If a donation is provided that spans x goals then the representative
    will need to provide x updates prior to receiving their next release
    """
    # Whether or not the donation has been delivered or has just been pledged
    # False if Pledged and True if executed upon
    completed = BooleanProperty(default=False)
    # Set as a float to enable change to be specified. Even though from an
    # interface perspective we probably want to maintain that donations of
    # 5, 10, 100, etc are made.
    amount = IntegerProperty()

    # relationships
    # donated_for is what goal the user actually pledged the donation to.
    donated_for = RelationshipTo('sb_goals.neo_models.Goal', 'DONATED_FOR')
    # applied_to are the goals the donation was actually applied to. This in
    # most circumstances will be the same goal as was donated for but may
    # cover multiple goals based on the donation amount.
    applied_to = RelationshipTo('sb_goals.neo_models.Goal', 'APPLIED_TO')
    owned_by = RelationshipTo('plebs.neo_models.Pleb', 'DONATED_FROM')
    # Every donation must have a cause that it's donating to. We'll utilize
    # child donations to accomplish this but through using `cause` as the
    # naming convention we should be able to define all methods at this level
    campaign = RelationshipTo('sb_campaigns.neo_models.Campaign', 'DONATED_TO')


class PoliticalDonation(Donation):
    """
    In the serializer need to set a max of 2,600 and check how much the owner
    has given to the specified candidate as you can only donate 2,600 per
    election. Should be able to utilize the created dates to determine when
    we can reset the counter
    """
    # TODO not sure if there are any special attributes that a political
    # donation needs over a standard donation.
    pass
