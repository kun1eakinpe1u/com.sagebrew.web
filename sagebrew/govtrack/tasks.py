from celery import shared_task
from requests import get
from datetime import datetime

from neomodel import CypherException, DoesNotExist

from .utils import populate_gt_roles_util
from govtrack.neo_models import (GTPerson, GTCommittee,
                                 GT_RCVotes, GTVoteOption)


@shared_task()
def populate_gt_role(requesturl):
    """
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTRole object then
    saves it
    to the neo4j server.
    """
    population = populate_gt_roles_util(requesturl)
    if isinstance(population, Exception) is True:
        raise populate_gt_role.retry(exc=population, countdown=3,
                                     max_retries=None)
    return True


@shared_task()
def populate_gt_person(requesturl):
    """
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTPerson object then
    saves it to the
    neo4j server.

    Will eventually create relationships between GTPerson and GTRole.
    """
    person_request = get(requesturl)
    person_data_dict = person_request.json()
    for person in person_data_dict['objects']:
        try:
            GTPerson.nodes.get(gt_id=person["id"])
        except(GTPerson.DoesNotExist, DoesNotExist):
            person["birthday"] = datetime.strptime(person["birthday"],
                                                   '%Y-%m-%d')
            person["gt_id"] = person["id"]
            person.pop("id", None)
            my_person = GTPerson(**person)
            try:
                my_person.save()
            except (CypherException, IOError) as e:
                populate_gt_person.retry(exc=e, countdown=3, max_retries=None)
        except (CypherException, IOError) as e:
            populate_gt_person.retry(exc=e, countdown=3, max_retries=None)
    return True


@shared_task()
def populate_gt_committee(requesturl):
    """
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GTCommittee object then
    saves
    to the neo4j server.

    Will eventually create relationships between sub committees.
    """
    committee_request = get(requesturl)
    committee_data_dict = committee_request.json()
    for committee in committee_data_dict['objects']:
        try:
            GTCommittee.nodes.get(committee_id=committee["id"])
        except(GTCommittee.DoesNotExist, DoesNotExist):
            committee["committee_id"] = committee["id"]
            committee.pop("id", None)
            committee.pop("committee", None)
            my_committee = GTCommittee(**committee)
            try:
                my_committee.save()
            except (CypherException, IOError) as e:
                populate_gt_committee.retry(exc=e,
                                            countdown=3, max_retries=None)
        except (CypherException, IOError) as e:
            populate_gt_committee.retry(exc=e, countdown=3,
                                        max_retries=None)
    return True


@shared_task()
def populate_gt_votes(requesturl):
    """
    This function takes a url which can be converted into a .json file. It
    then converts
    the json into a dict and creates and populates a GT_RCVotes object. It
    then also creates
    multiple GTVoteOption objects which are related to the GT_RCVotes object
    that was created.
    It also creates the relationship between the GT_RCVotes and GTVoteOption.
    """
    vote_request = get(requesturl)
    vote_data_dict = vote_request.json()
    my_votes = []
    for vote in vote_data_dict['objects']:
        try:
            GT_RCVotes.nodes.get(vote_id=vote["id"])
        except(GT_RCVotes.DoesNotExistm, DoesNotExist):
            for voteoption in vote['options']:
                try:
                    GTVoteOption.nodes.get(option_id=voteoption["id"])
                except GTVoteOption.DoesNotExist:
                    voteoption["option_id"] = voteoption["id"]
                    voteoption.pop("id", None)
                    my_vote_option = GTVoteOption(**voteoption)
                    my_vote_option.save()
                    my_votes.append(my_vote_option)
            vote.pop("options", None)
            vote["vote_id"] = vote["id"]
            vote.pop("id", None)
            vote["category_one"] = vote["category"]
            vote.pop("category", None)
            my_vote = GT_RCVotes(**vote)
            try:
                my_vote.save()
                for item in my_votes:
                    my_vote.option.connect(item)
            except (CypherException, IOError) as e:
                raise populate_gt_votes.retry(exc=e, countdown=3,
                                              max_retries=None)
            my_votes = []
        except(CypherException, IOError) as e:
            raise populate_gt_votes.retry(exc=e, countdown=3, max_retries=None)
    return True
