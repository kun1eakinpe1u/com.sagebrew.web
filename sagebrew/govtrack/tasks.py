from celery import shared_task
from requests import get
from govtrack.models import SRole , Person , GTBill , GTVotes , GTVoteOptions

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
            my_vote = GTVotes(**vote)
            my_vote.save()




