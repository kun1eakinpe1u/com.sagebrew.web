from elasticsearch import Elasticsearch, NotFoundError

from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.cache import cache
from django.template import RequestContext
from django.conf import settings

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.generics import (RetrieveUpdateDestroyAPIView)

from neomodel import db

from sagebrew import errors

from api.utils import request_to_api
from api.permissions import IsSelfOrReadOnly, IsSelf
from sb_base.utils import get_filter_params
from sb_base.neo_models import SBContent
from sb_base.serializers import MarkdownContentSerializer
from sb_questions.neo_models import Question
from sb_questions.serializers import QuestionSerializerNeo
from sb_votes.serializers import VoteSerializer
from sb_public_official.serializers import PublicOfficialSerializer

from .serializers import (UserSerializer, PlebSerializerNeo, AddressSerializer,
                          FriendRequestSerializer)
from .neo_models import Pleb, Address, FriendRequest
from .utils import get_filter_by


class AddressViewSet(viewsets.ModelViewSet):
    """
    This ViewSet provides all of the addresses associated with the currently
    authenticated user. We don't want to enable users to view all addresses
    utilized on the site from an endpoint but this endpoint allows for users
    to see and modify their own as well as create new ones.

    Limitations:
    Currently we don't have a way to determine which address is the current
    address. We also don't have an interface to generate additional addresses
    so the address input during registration is the only address ever listed
    even though this should not be expected as in the future the list will
    grow as we all things like hometown, previous residences, and additional
    homes to be listed.
    """
    serializer_class = AddressSerializer
    lookup_field = 'object_uuid'

    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address) RETURN b' % (self.request.user.username)
        res, col = db.cypher_query(query)
        return [Address.inflate(row[0]) for row in res]

    def get_object(self):
        query = 'MATCH (a:Pleb {username: "%s"})-[:LIVES_AT]->' \
                '(b:Address {object_uuid: "%s"}) RETURN b' % (
                    self.request.user.username, self.kwargs[self.lookup_field])
        res, col = db.cypher_query(query)
        return Address.inflate(res[0][0])

    def perform_create(self, serializer):
        pleb = Pleb.get(self.kwargs[self.lookup_field])
        instance = serializer.save()
        instance.owned_by.connect(pleb)
        instance.save()
        pleb.address.connect(instance)
        pleb.save()
        cache.set(pleb.username, pleb)


class UserViewSet(viewsets.ModelViewSet):
    """
    This ViewSet provides interactions with the base framework user. If you
    need to create/destroy/modify this is where it should be done.

    Limitations:
    Currently we still manage user creation through a different interface
    in the registration application. Eventually we'll look to utilize this
    endpoint from the registration application to create the user and create
    a more uniform user creation process that can be used throughout our
    different systems.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'

    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
        es = Elasticsearch(settings.ELASTIC_SEARCH_HOST)
        try:
            es.delete(index="full-search-base", doc_type='profile',
                      id=instance.username)
        except NotFoundError:
            pass
        logout(self.request)
        # TODO we can also go and delete the pleb and content from here
        # or require additional requests but think we could spawn a task
        # that did all that deconstruction work rather than requiring an
        # app the hit a thousand endpoints.


class ProfileViewSet(viewsets.ModelViewSet):
    """
    This endpoint provides information for each of the registered users. It
    should not be used for creating users though as we lean on the Framework
    to accomplish user creation and authentication. This however is where all
    non-base attributes can be accessed. Users can access any other user's
    information as long as their authenticated but are limited to Read access
    if they are not the owner of the profile.

    Limitations:
    Currently we don't have fine grained permissions that enable us to restrict
    access to certain fields based on friendship status or user set permissions.
    We instead manage this in the frontend and only allow users browsing the
    web interface to see certain information. This is all done in the template
    though and any tech savvy person will still be able to check out the
    endpoint for the information. We'll want to eventually limit that here
    or in the serializer rather than higher up on the stack.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    queryset = Pleb.nodes.all()
    permission_classes = (IsAuthenticated, IsSelfOrReadOnly)
    pagination_class = LimitOffsetPagination

    def get_object(self):
        return Pleb.get(self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        """
        Currently a profile is generated for a user when the base user is
        created. We currently don't support creating a profile through an
        endpoint due to the confirmation process and links that need to be
        made.
        :param request:
        :return:
        """
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def solutions(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def questions(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (a:Pleb {username: "%s"})-[:OWNS_QUESTION]->' \
                '(b:Question) WHERE b.to_be_deleted=false' \
                ' %s RETURN b' % (username, additional_params)
        res, col = db.cypher_query(query)
        queryset = [Question.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = QuestionSerializerNeo(page, many=True,
                                           context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'])
    def public_content(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (b:`SBPublicContent`)-[:OWNED_BY]->(a:Pleb ' \
                '{username: "%s"}) ' \
                'WHERE b.to_be_deleted=false ' \
                ' %s RETURN b' % (username, additional_params)

        res, col = db.cypher_query(query)
        queryset = [SBContent.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = MarkdownContentSerializer(page, many=True,
                                               context={'request': request})
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'])
    def friend(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def unfriend(self, request, username=None):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @detail_route(methods=['get'])
    def friends(self, request, username=None):
        # Discuss, does it make more sense to have friends here or have a
        # separate endpoint /v1/friends/ that just
        # lists all the friends for the user who is making the query? I think
        # both places are valid. /v1/profiles/username/friends does enable you
        # to look at friends of friends more easily
        # However /v1/friends/username/ allows for a simpler defriend and
        # accessing method as you're able to go from
        # /v1/friends/ to /v1/friends/username/ to your method rather than
        # /v1/profiles/username/friends/ to /v1/profiles/username/ to your
        # method. But maybe we make both available.
        query = 'MATCH (a:Pleb {username: "%s"})-' \
                '[:FRIENDS_WITH {currently_friends: true}]->' \
                '(b:Pleb) RETURN b' % (username)
        res, col = db.cypher_query(query)
        queryset = [Pleb.inflate(row[0]) for row in res]
        html = self.request.query_params.get('html', 'false')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True,
                                         context={'request': request})
        if html == 'true':
            html_array = []
            for item in serializer.data:
                context = RequestContext(request, item)
                item['page_user_username'] = username
                html_array.append(render_to_string('friend_block.html',
                                                   context))
            return self.get_paginated_response(html_array)
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def friend_requests(self, request, username=None):
        # TODO we should probably make some sort of "notification" list view
        # or it can be more specific and be a friend request list view. But
        # that way we can get the pagination functionality easily and break out
        # html rendering. We can wait on it though until we transition to
        # JS framework
        if request.user.username != username:
            return Response({"detail":
                             "You can only get your own friend requests"},
                            status=status.HTTP_401_UNAUTHORIZED)
        query = "MATCH (f:FriendRequest)-[:REQUEST_TO]-" \
                "(p:Pleb {username: '%s'}) RETURN f " \
                "ORDER BY f.time_sent LIMIT 7" % (username)
        res, col = db.cypher_query(query)
        queryset = [FriendRequest.inflate(row[0]) for row in res]

        friend_requests = FriendRequestSerializer(queryset, many=True,
                                                  context={"request": request})
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            html = render_to_string('friend_request_wrapper.html',
                                    {"requests": friend_requests.data})
            return Response(html, status=status.HTTP_200_OK)
        return Response(friend_requests.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def notifications(self, request, username=None):
        notifications = self.get_object().get_notifications()
        expand = self.request.QUERY_PARAMS.get('expand', "false").lower()
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            expand = 'true'
        for notification in notifications:
            if expand == "false":
                notification["from"] = reverse(
                    'profile-detail',
                    kwargs={'username': notification["notification_from"][
                        "username"]},
                    request=request)
            else:
                friend_url = reverse(
                    'profile-detail', kwargs={
                        'username': notification["notification_from"][
                            "username"]},
                    request=request)
                response = request_to_api(friend_url, request.user.username,
                                          req_method="GET")
                notification["from"] = response.json()
        if html == 'true':
            sorted(notifications, key=lambda k: k['time_sent'], reverse=True)
            notifications = notifications[:6]
            html = render_to_string('notifications.html',
                                    {"notifications": notifications})
            return Response(html, status=status.HTTP_200_OK)
        return Response(notifications, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated,))
    def reputation(self, request, username=None):
        return Response({"reputation": self.get_object().reputation},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated))
    def senators(self, request, username=None):
        senators = self.get_object().senators.all()
        if len(senators) == 0:
            return Response("<small>Sorry we could not find your "
                            "Senators. Please alert us to our error!"
                            "</small>", status=status.HTTP_200_OK)
        html = self.request.query_params.get('html', 'false').lower()
        if html == 'true':
            sen_html = []
            for sen in senators:
                sen_html.append(
                    render_to_string('sb_home_section/sb_senator_block.html',
                                     PublicOfficialSerializer(sen).data))
            return Response(sen_html, status=status.HTTP_200_OK)
        return Response(senators, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated))
    def house_rep(self, request, username=None):
        try:
            house_rep = self.get_object().house_rep.all()[0]
        except IndexError:
            return Response("<small>Sorry we could not find your "
                            "representative. Please alert us to our error!"
                            "</small>", status=status.HTTP_200_OK)
        html = self.request.QUERY_PARAMS.get('html', 'false').lower()
        if html == 'true':
            house_rep_html = render_to_string(
                'sb_home_section/sb_house_rep_block.html',
                PublicOfficialSerializer(house_rep).data)
            return Response(house_rep_html, status=status.HTTP_200_OK)
        return Response(house_rep, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def address(self, request, username=None):
        single_object = self.get_object()
        try:
            address = single_object.address.all()[0]
        except(IndexError):
            return Response(errors.CYPHER_INDEX_EXCEPTION,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        address_serializer = AddressSerializer(address,
                                               context={'request': request})
        return Response(address_serializer.data, status=status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def is_beta_user(self, request, username=None):
        return Response({'is_beta_user': self.get_object().is_beta_user()},
                        status.HTTP_200_OK)

    @detail_route(methods=['get'], permission_classes=(IsAuthenticated, IsSelf))
    def votes(self, request, username=None):
        filter_by = request.query_params.get('filter', "")
        try:
            additional_params = get_filter_params(filter_by, SBContent())
        except(IndexError, KeyError, ValueError):
            return Response(errors.QUERY_DETERMINATION_EXCEPTION,
                            status=status.HTTP_400_BAD_REQUEST)
        query = 'MATCH (b:`SBPublicContent`)-[:OWNED_BY]->(a:Pleb ' \
                '{username: "%s"}) ' \
                'WHERE b.to_be_deleted=false ' \
                ' %s RETURN b' % (username, additional_params)

        res, col = db.cypher_query(query)
        queryset = [SBContent.inflate(row[0]) for row in res]

        page = self.paginate_queryset(queryset)
        serializer = VoteSerializer(page, many=True,
                                    context={'request': request})
        return self.get_paginated_response(serializer.data)


class MeRetrieveUpdateDestroy(RetrieveUpdateDestroyAPIView):
    """
    This endpoint provides the ability to get information regarding the
    currently authenticated user. This way AJAX, Ember, and other front end
    systems don't need to know what username they should bake into a
    /profile/ url to get information on the signed in user.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "username"
    permission_classes = (IsAuthenticated, IsSelf)

    def get_object(self):
        return Pleb.get(self.request.user.username)


class FriendRequestViewSet(viewsets.ModelViewSet):
    """
    This ViewSet enables the user that is currently authenticated to view and
    manage their friend requests. Instead of making a method view on a specific
    profile we took this approach to gain easy pagination and so that the entire
    suite of managing an object could be utilized.
    """
    serializer_class = FriendRequestSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        filter_by = self.request.query_params.get("filter", "")
        filtered = get_filter_by(filter_by)
        query = "MATCH (p:Pleb {username:'%s'})-%s-(r:FriendRequest) RETURN r" \
                % (self.request.user.username, filtered)
        res, col = db.cypher_query(query)
        return [FriendRequest.inflate(row[0]) for row in res]

    def get_object(self):
        return FriendRequest.nodes.get(
            object_uuid=self.kwargs[self.lookup_field])

    def create(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)


class FriendManager(RetrieveUpdateDestroyAPIView):
    """
    The Friend Manager expects to be placed on the /me endpoint so that it
    can assume to grab the currently signed in user to manage friends for.
    """
    serializer_class = PlebSerializerNeo
    lookup_field = "friend_username"
    permission_classes = (IsAuthenticated, IsSelf)

    def get_object(self):
        return Pleb.get(self.kwargs[self.lookup_field])

    def update(self, request, *args, **kwargs):
        return Response({"detail": "TBD"},
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    def destroy(self, request, *args, **kwargs):
        friend = self.get_object()
        profile = Pleb.get(request.user.username)
        # TODO: Change this to modifying the relationship manager rather than
        # just disconnecting

        profile.friends.disconnect(friend)
        friend.friends.disconnect(profile)

        return Response({'detail': 'success'},
                        status=status.HTTP_204_NO_CONTENT)
