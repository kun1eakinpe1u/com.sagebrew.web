from celery import shared_task
from requests import get
from govtrack.models import SRole , Person , GTBill , GTVotes , GTVoteOptions
from govtrack.neo_models import GTPerson, GTRole


@shared_task()
def populate_role(requesturl):
    role_request = get(requesturl)
    role_data_dict = role_request.json()
    for representative in role_data_dict['objects']:
        my_person = Person.objects.create(**representative['person'])
        my_person.save()
        representative["person"] = my_person
        new_rep = SRole.objects.create(**representative)
        new_rep.save()



@shared_task()
def populate_gt_bills(requesturl):
    bill_request = get(requesturl)
    bill_data_dict = bill_request.json()
    for bill in bill_data_dict['objects']:
        try:
            my_bill = GTBill.objects.get(id=bill["id"])
        except GTBill.DoesNotExist:
            bill["sponsor"] = bill["sponsor"]["id"]
            bill["sponsor_role"] = bill["sponsor_role"]["id"]
            my_bill = GTBill(**bill)
            my_bill.save()


@shared_task()
def populate_gt_votes(requesturl):
    vote_request = get(requesturl)
    vote_data_dict = vote_request.json()
    options = []
    for vote in vote_data_dict['objects']:
        try:
            my_vote = GTVotes.objects.get(vote_id=vote["id"])
        except GTVotes.DoesNotExist:
            for vote_option in vote['options']:
                try:
                    my_vote_option = GTVoteOptions.objects.get(vote_options_id=vote_option["id"])
                except GTVoteOptions.DoesNotExist:
                    vote_option["vote_options_id"] = vote_option["id"]
                    vote_option.pop("id", None)
                    my_vote_option = GTVoteOptions(**vote_option)
                    my_vote_option.save()
                    options.append(my_vote_option)
            vote.pop("options",None)
            vote["vote_id"] = vote["id"]
            vote.pop("id", None)
            #vote["datecreated"] = vote["created"]
            my_vote = GTVotes(**vote)
            my_vote.save()
            for option in options:
                my_vote.options.add(option)



@shared_task()
def populate_gt_role(requesturl):
    role_request = get(requesturl)
    role_data_dict = role_request.json()
    for rep in role_data_dict['objects']:
        try:
            my_role = GTRole.index.get(id=rep["id"])
        except GTRole.DoesNotExist:
            my_person = GTPerson(**rep['person'])
            my_person.save()
            rep["person"] = my_person
            my_role = GTRole(**rep)
            my_role.save()



@shared_task()
def populate_gt_person(requesturl):
    person_request = get(requesturl)
    person_data_dict = person_request.json()
    for person in person_data_dict['objects']:
        try:
            my_person = GTPerson.index.get(id=person["id"])
        except GTPerson.DoesNotExist:
            my_person = GTPerson()
            my_person.bioguideid = person["bioguideid"]
            my_person.birthday = person["birthday"]
            my_person.cspanid = person["cspanid"]
            my_person.firstname = person["firstname"]
            my_person.gender = person["gender"]
            my_person.gender_label = person["gender_label"]
            my_person.id = person["id"]
            my_person.lastname = person["lastname"]
            my_person.link = person["link"]
            my_person.middlename = person["middlename"]
            my_person.name = person["name"]
            my_person.namemod = person["namemod"]
            my_person.nickname = person["nickname"]
            my_person.osid = person["osid"]
            my_person.pvsid = person["pvsid"]
            my_person.sortname = person["sortname"]
            my_person.twitterid = person["twitterid"]
            my_person.youtubeid = person["youtubeid"]
            my_person.save()






