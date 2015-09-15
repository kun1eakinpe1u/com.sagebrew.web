from django.template import RequestContext
from django.template.loader import render_to_string

from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status

from neomodel import db

from sb_campaigns.neo_models import Position

from .serializers import LocationSerializer, LocationManagerSerializer
from .neo_models import Location

from logging import getLogger
logger = getLogger('loggly_logs')


class LocationList(viewsets.ReadOnlyModelViewSet):
    serializer_class = LocationSerializer
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        query = 'MATCH (l:`Location`) RETURN l'
        res, col = db.cypher_query(query)
        return [Location.inflate(row[0]) for row in res]

    def get_object(self):
        return Location.get(object_uuid=self.kwargs[self.lookup_field])

    @list_route(methods=['post'],
                serializer_class=LocationManagerSerializer,
                permission_classes=(IsAuthenticated,))
    def add(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer = serializer.save()
            return Response(LocationSerializer(serializer).data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_positions(request, name=None):
    query = 'MATCH (l:Location {name:"%s"})-[:POSITIONS_AVAILABLE]->' \
            '(p1:Position) WITH l, p1 OPTIONAL MATCH (l)-[:ENCOMPASSES]->' \
            '(l2:Location)-[:POSITIONS_AVAILABLE]->(p2:Position) WITH ' \
            'l2, p2, l, p1 ' \
            'OPTIONAL MATCH (l2)-' \
            '[:ENCOMPASSES]->(l3:Location)-[:POSITIONS_AVAILABLE]' \
            '->(p3:Position) ' \
            'RETURN p1.object_uuid as object_uuid1, ' \
            'p2.object_uuid as object_uuid2, ' \
            'p3.object_uuid as object_uuid3' % name
    res, _ = db.cypher_query(query)
    local = []
    for row in res:
        if row.object_uuid3 is not None:
            local.append(row.object_uuid3)
    return Response({"senator": res[0].object_uuid1,
                     "house_reps": [row.object_uuid2 for row in res],
                     "local": local},
                    status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def render_positions(request, name=None):
    positions = get_positions(request, name).data
    senator = Position.get_full_name(positions['senator'])
    representatives = []
    for representative in positions['house_reps']:
        representatives.append(Position.get_full_name(representative))
    for representative in positions['local']:
        representatives.append(Position.get_full_name(representative))

    representatives.append(senator)
    position_html = [render_to_string('position_selector.html',
                                      {'name': rep_name,
                                       "state_name": "".join(name.split())},
                                      context_instance=RequestContext(request))
                     for rep_name in representatives]
    return Response(position_html, status=status.HTTP_200_OK)
