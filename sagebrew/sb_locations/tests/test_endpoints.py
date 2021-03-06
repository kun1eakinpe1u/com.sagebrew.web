#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=utf-8
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.cache import cache

from neomodel import db

from rest_framework import status
from rest_framework.test import APITestCase

from plebs.neo_models import Pleb
from sb_registration.utils import create_user_util_test

from sb_locations.neo_models import Location
from sb_quests.neo_models import Position


wixom_data = {
    "address_components": [
        {
            "long_name": "Wixom",
            "short_name": "Wixom",
            "types": [
                "locality",
                "political"
            ]
        },
        {
            "long_name": "Oakland County",
            "short_name": "Oakland County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
        },
        {
            "long_name": "Michigan",
            "short_name": "MI",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
        },
        {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
        }
    ],
    "adr_address": "<span class=\"locality\">Wixom</span>, "
                   "<span class=\"region\">MI</span>, "
                   "<span class=\"country-name\">USA</span>",
    "formatted_address": "Wixom, MI, USA",
    "geometry": {
        "location": {},
        "viewport": {
            "O": {
                "O": 42.493165,
                "j": 42.55855589999999
            },
            "j": {
                "j": -83.558674,
                "O": -83.507566
            }
        }
    },
    "icon": "https://maps.gstatic.com/mapfiles/place_api/icons/geocode-71.png",
    "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
    "name": "Wixom",
    "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
    "reference": "CnRrAAAAd8ZPXfASBM6FFtdy7mckkorluFIIsJlBesOwOUtRqhIOhWPZJ"
                 "i8ul4sx8pozfeSSMYidyRbS37IkNcMJ2e76UsBnvrpWr-wRMKo-jfzCrJu"
                 "YQIxQ_1j40TTd_cZSMgQXVQgnqn940GYDuYTbpNT8thIQYBVqsZV4thkz"
                 "ZT90o9E0DBoUrELXmJ3GdZlCgHjdowsRZlQIDkk",
    "scope": "GOOGLE",
    "types": [
        "locality",
        "political"
    ],
    "url": "https://maps.google.com/?q=Wixom,+MI,+USA&ftid=0x8824a620614c1b"
           "ef:0x5f1e999bcb411664",
    "vicinity": "Wixom",
    "html_attributions": []
}


springfield_data = [
    {
        'long_name': 'Springfield',
        'short_name': 'Springfield',
        'types': [
            'locality',
            'political'
        ],
    },
    {
        'long_name': 'Lee',
        'types': ['administrative_area_level_3', 'political'],
        'short_name': 'Lee'
    },
    {
        'long_name': 'Fairfax County',
        'types': [u'administrative_area_level_2', u'political'],
        'short_name': u'Fairfax County'
    },
    {
        'long_name': 'Virginia',
        'types': ['administrative_area_level_1', 'political'],
        'short_name': 'VA'
    },
    {
        'long_name': 'United States',
        'types': [u'country', u'political'],
        'short_name': u'US'
    }
]


class LocationEndpointTests(APITestCase):

    def setUp(self):
        self.unit_under_test_name = 'location'
        self.email = "success@simulator.amazonses.com"
        create_user_util_test(self.email)
        self.pleb = Pleb.nodes.get(email=self.email)
        self.user = User.objects.get(email=self.email)
        self.url = "http://testserver"
        query = 'MATCH (a:Position) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        query = 'MATCH (a:Location) OPTIONAL MATCH (a)-[r]-() DELETE a, r'
        db.cypher_query(query)
        self.location = Location(name="Michigan").save()
        self.city = Location(name="Walled Lake").save()
        self.senator = Position(name="Senator").save()
        self.house_rep = Position(name="House Rep").save()
        self.school = Position(name="School Board", level="local").save()
        self.location.encompasses.connect(self.city)
        self.city.encompassed_by.connect(self.location)
        self.senator.location.connect(self.location)
        self.house_rep.location.connect(self.location)
        self.school.location.connect(self.city)
        cache.clear()

    def test_unauthorized(self):
        url = reverse('location-list')
        response = self.client.post(url, {}, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_save_int_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 98897965, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_string_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 'asfonosdnf', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_list_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, [], format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_save_float_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.post(url, 1.010101010, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_on_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.post(url, data={}, format='json')
        response_data = {
            'status_code': status.HTTP_405_METHOD_NOT_ALLOWED,
            'detail': 'Method "POST" not allowed.'
        }
        self.assertEqual(response.data, response_data)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_name(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['name'], self.location.name)

    def test_detail_encompasses(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['encompasses'], [self.city.object_uuid])

    def test_detail_encompassed_by(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['encompassed_by'], [])

    def test_detail_geo_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertFalse(response.data['geo_data'])

    def test_detail_positions(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertIn(self.house_rep.object_uuid, response.data['positions'])
        self.assertIn(self.senator.object_uuid, response.data['positions'])

    def test_detail_id(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['id'], self.location.object_uuid)

    def test_detail_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-detail',
                      kwargs={'object_uuid': self.location.object_uuid})
        response = self.client.get(url)

        self.assertEqual(response.data['type'], self.unit_under_test_name)

    def test_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_non_admin(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": "Michigan",
            "encompassed_by_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_anon(self):
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": "Michigan",
            "encompassed_by_uuid": ""
        }, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED,
                                             status.HTTP_403_FORBIDDEN])

    def test_add_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom",
            "geo_data": None,
            "encompassed_by_name": self.location.name,
            "encompassed_by_uuid": ""
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Wixom')
        self.assertEqual(response.data['geo_data'], False)
        self.assertIn(self.location.object_uuid,
                      response.data['encompassed_by'])

    def test_add_admin_unicode(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Iñtërnâtiônàlizætiøn2",
            "geo_data": None,
            "encompassed_by_name": self.location.name,
            "encompassed_by_uuid": ""
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Internationalizaetion2')
        self.assertEqual(response.data['geo_data'], False)
        self.assertIn(self.location.object_uuid,
                      response.data['encompassed_by'])

    def test_add_get(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.get(url)
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_add_uuid(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "City of Wixom",
            "geo_data": None,
            "encompassed_by_name": "",
            "encompassed_by_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'City of Wixom')
        self.assertEqual(response.data['geo_data'], False)
        self.assertIn(self.location.object_uuid,
                      response.data['encompassed_by'])

    def test_add_already_exists(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        post_info = {
            "name": "City of Wixom2",
            "geo_data": None,
            "encompassed_by_name": "",
            "encompassed_by_uuid": self.location.object_uuid
        }
        self.client.post(url, post_info, format='json')
        response = self.client.post(url, post_info, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['name'],
                         [u'Sorry looks like a Location with that Name '
                          u'already Exists'])

    def test_add_invalid_serializer(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add')
        response = self.client.post(url, {
            "name": "Wixom City",
            "encompassed_by_uuid": self.location.object_uuid
        }, format='json')
        self.user.is_staff = False
        self.user.save()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_external_id_with_admin_3_and_locality(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add-external-id')
        response = self.client.post(url, {
            "place_id": "ChIJnTrlhehNtokRBKX6FiRv52c",
            "address_components": springfield_data
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Springfield')

    def test_add_external_id_with_locality(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add-external-id')
        response = self.client.post(url, wixom_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Wixom')

    def test_add_external_id_does_not_exist(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('location-add-external-id')
        response = self.client.post(url, {
            "place_id": "ChIJkRBFiR1234",
            'address_components': []
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['place_id'],
                         ["We could not find that Place ID"])

    def test_cache_location(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        data = {
            "address_components": [
                {
                    "long_name": "Wixom",
                    "short_name": "Wixom",
                    "types": [
                        "locality",
                        "political"
                    ]
                },
                {
                    "long_name": "Oakland County",
                    "short_name": "Oakland County",
                    "types": [
                        "administrative_area_level_2",
                        "political"
                    ]
                },
                {
                    "long_name": "Michigan",
                    "short_name": "MI",
                    "types": [
                        "administrative_area_level_1",
                        "political"
                    ]
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": [
                        "country",
                        "political"
                    ]
                }
            ],
            "adr_address": "",
            "formatted_address": "Wixom, MI, USA",
            "geometry": {
                "location": {},
                "viewport": {
                    "O": {
                        "O": 42.493165,
                        "j": 42.55855589999999
                    },
                    "j": {
                        "j": -83.558674,
                        "O": -83.507566
                    }
                }
            },
            "icon": "https://maps.gstatic.com/mapfiles/place_api/"
                    "icons/geocode-71.png",
            "id": "20c67ea90c3088cc7d5fdd08dc7ccd170559a4fe",
            "name": "Wixom",
            "place_id": "ChIJ7xtMYSCmJIgRZBZBy5uZHl8",
            "reference": "-wRMKo-",
            "scope": "GOOGLE",
            "types": [
                "locality",
                "political"
            ],
            "url": "",
            "vicinity": "Wixom",
            "html_attributions": []
        }
        url = reverse('location-cache')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(cache.get(data['place_id']), data)

    def test_cache_location_bad_request(self):
        cache.clear()
        self.client.force_authenticate(user=self.user)
        data = {
            "address_components": [
                {
                    "long_name": "Wixom",
                    "short_name": "Wixom",
                    "types": [
                        "locality",
                        "political"
                    ]
                },
                {
                    "long_name": "Oakland County",
                    "short_name": "Oakland County",
                    "types": [
                        "administrative_area_level_2",
                        "political"
                    ]
                },
                {
                    "long_name": "Michigan",
                    "short_name": "MI",
                    "types": [
                        "administrative_area_level_1",
                        "political"
                    ]
                },
                {
                    "long_name": "United States",
                    "short_name": "US",
                    "types": [
                        "country",
                        "political"
                    ]
                }
            ]
        }
        url = reverse('location-cache')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNone(cache.get("ChIJ7xtMYSCmJIgRZBZBy5uZHl8"))
