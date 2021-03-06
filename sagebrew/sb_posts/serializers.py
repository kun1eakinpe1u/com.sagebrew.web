import bleach
import pytz
from uuid import uuid1
from datetime import datetime

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError

from neomodel import DoesNotExist

from api.utils import gather_request_data
from sb_base.serializers import ContentSerializer, validate_is_owner
from plebs.serializers import PlebSerializerNeo
from plebs.neo_models import Pleb
from sb_uploads.neo_models import UploadedObject, URLContent

from .neo_models import Post


class PostSerializerNeo(ContentSerializer):
    content = serializers.CharField(allow_blank=True)
    href = serializers.HyperlinkedIdentityField(view_name='post-detail',
                                                lookup_field="object_uuid")
    images = serializers.ListField(write_only=True, required=False)
    included_urls = serializers.ListField(write_only=True, required=False)

    url_content = serializers.SerializerMethodField()
    uploaded_objects = serializers.SerializerMethodField()
    first_url_content = serializers.SerializerMethodField()
    wall_owner_profile = serializers.SerializerMethodField()

    def validate(self, data):
        if data.get('images', None) is not None and \
                len(data.get('images', [])) > 0:
            return data
        else:
            if data.get('content') is None or data.get('content') == '':
                raise ValidationError(
                    {'content': 'This field may not be blank'})

        return data

    def create(self, validated_data):
        request = self.context["request"]
        owner = Pleb.get(request.user.username)
        wall_owner = validated_data.pop('wall_owner_profile', None)
        images = validated_data.pop('images', [])
        included_urls = validated_data.pop('included_urls', [])
        uuid = str(uuid1())
        url = reverse('profile_page', kwargs={
            'pleb_username': request.user.username}, request=request)
        href = reverse('post-detail', kwargs={'object_uuid': uuid},
                       request=request)
        post = Post(owner_username=owner.username,
                    wall_owner_username=wall_owner.username,
                    object_uuid=uuid, url=url, href=href,
                    **validated_data).save()
        post.owned_by.connect(owner)
        wall = wall_owner.get_wall()
        post.posted_on_wall.connect(wall)
        wall.posts.connect(post)
        [post.uploaded_objects.connect(
            UploadedObject.nodes.get(object_uuid=image)) for image in images]
        for url in included_urls:
            try:
                post.url_content.connect(URLContent.nodes.get(url=url))
            except (DoesNotExist, URLContent.DoesNotExist):
                pass
        return post

    def update(self, instance, validated_data):
        validate_is_owner(self.context.get('request', None), instance)
        instance.content = bleach.clean(validated_data.get(
            'content', instance.content))
        instance.last_edited_on = datetime.now(pytz.utc)
        instance.save()
        included_urls = validated_data.pop('included_urls', [])
        for url in included_urls:
            try:
                instance.url_content.connect(URLContent.nodes.get(url=url))
            except (DoesNotExist, URLContent.DoesNotExist):
                pass
        return instance

    def get_url(self, obj):
        request, _, _, _, expedite = gather_request_data(self.context)
        if expedite == "true":
            return None
        return obj.get_url(request)

    def get_wall_owner_profile(self, obj):
        request, expand, _, _, expedite = gather_request_data(self.context)
        if self.context.get('force_expand', False):
            return PlebSerializerNeo(
                obj.get_wall_owner_profile(), context={'request': request}).data
        if expedite == "true":
            return None
        if isinstance(obj, dict) is True:
            return obj
        wall_owner = obj.get_wall_owner_profile()
        if expand == "true":
            profile_dict = PlebSerializerNeo(
                wall_owner, context={'request': request}).data
        else:
            profile_dict = reverse('profile-detail',
                                   kwargs={"username": wall_owner.username},
                                   request=request)
        return profile_dict

    def get_uploaded_objects(self, obj):
        return obj.get_uploaded_objects()

    def get_url_content(self, obj):
        return obj.get_url_content()

    def get_first_url_content(self, obj):
        return obj.get_url_content(single=True)


class PostEndpointSerializerNeo(PostSerializerNeo):
    wall = serializers.CharField(write_only=True, required=False)
