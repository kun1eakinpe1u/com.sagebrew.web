from django.conf import settings

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from neomodel import db

from .neo_models import Product, Giftlist
from .serializers import GiftlistSerializer


class GiftListViewSet(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "object_uuid"
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = GiftlistSerializer

    def get_object(self):
        query = 'MATCH (mission:Mission {object_uuid:"%s"})<-[:LIST_FOR]-' \
                '(g:Giftlist) RETURN g' % self.kwargs[self.lookup_field]
        res, _ = db.cypher_query(query)
        [row[0].pull() for row in res]
        return Giftlist.inflate(res.one)

