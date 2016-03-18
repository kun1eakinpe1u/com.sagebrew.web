import pytz
import stripe
import calendar
from uuid import uuid1
from datetime import datetime
from intercom import Intercom, Event

from django.conf import settings
from django.template.loader import render_to_string

from rest_framework import status, viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication

from api.utils import spawn_task
from plebs.neo_models import Pleb
from plebs.tasks import send_email_task
from sb_quests.neo_models import Quest
from sb_notifications.tasks import spawn_system_notification


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class AccountingViewSet(viewsets.ViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = ()

    def create(self, request):
        # TODO replace these with settings variables
        Intercom.app_id = 'jmz4pnau'
        Intercom.app_api_key = '24a76d234536a2115ebe4b4e8bfe3ed8aaaa6884'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            event = stripe.Event.retrieve(request.data['id'])
        except stripe.InvalidRequestError:
            return Response(status=status.HTTP_200_OK)

        if event['type'] == "invoice.payment_failed":
            try:
                customer = stripe.Customer.retrieve(
                    event['data']['object']['customer'])
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
            pleb = Pleb.nodes.get(email=customer['email'])
            email_data = {
                "source": "support@sagebrew.com",
                "to": [pleb.email],
                "subject": "Subscription Failure Notice",
                "html_content": render_to_string(
                    "email_templates/email_subscription_failure_notice.html",
                    {"billing_url":
                        reverse("quest_manage_billing",
                                kwargs={'username': pleb.username})})
            }
            spawn_task(task_func=send_email_task, task_param=email_data)
            return Response({"detail": "Invoice Payment Failed"},
                            status=status.HTTP_200_OK)
        if event['type'] == "account.updated":
            try:
                account = stripe.Account.retrieve(
                    event['data']['object']['id']
                )
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
            pleb = Pleb.nodes.get(email=account['email'])
            quest = Quest.get(pleb.username)
            if account['verification']['fields_needed']:
                quest.account_verification_fields_needed = \
                    account['verification']['fields_needed']

            if quest.account_verified != "verified" \
                    and account['legal_entity']['verification']['status'] \
                    == "verified":
                spawn_task(
                    task_func=spawn_system_notification,
                    task_param={
                        "to_plebs": [pleb.username],
                        "notification_id": str(uuid1()),
                        "url": reverse('quest',
                                       kwargs={'username': pleb.username}),
                        "action_name": "Your Quest has been verified!"
                    }
                )
            quest.account_verified = \
                account['legal_entity']['verification']['status']
            quest.account_verification_details = \
                str(account['legal_entity']['verification']['details'])
            if quest.account_first_updated is None \
                    and quest.account_verified != "verified":
                quest.account_first_updated = datetime.now(pytz.utc)
            quest.save()
            return Response({"detail": "Account Updated"},
                            status=status.HTTP_200_OK)
        if event['type'] == "transfer.failed":
            try:
                transfer = stripe.Transfer.retrieve(
                    event['data']['object']['id']
                )
                if transfer['type'] == 'stripe_account':
                    account = stripe.Account.retrieve(
                        transfer['destination']
                    )
            except stripe.InvalidRequestError:
                return Response(status=status.HTTP_200_OK)
            pleb = Pleb.nodes.get(email=account['email'])
            spawn_task(
                task_func=spawn_system_notification,
                task_param={
                    "to_plebs": [pleb.username],
                    "notification_id": str(uuid1()),
                    "url": reverse('quest_manage_banking',
                                   kwargs={"username": pleb.username}),
                    "action_name": "A transfer to your bank account has "
                                   "failed! Please review that your "
                                   "Quest Banking information is correct."
                }
            )
            Event.create(event_name="stripe-transfer-failed",
                         user_id=pleb.username,
                         created=calendar.timegm(
                             datetime.now(pytz.utc).utctimetuple())
            )
            return Response({"detail": "Transfer Failed"}, status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)
