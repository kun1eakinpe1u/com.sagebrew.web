import bleach
import string
import urlparse
import requests
import cStringIO
import HTMLParser
from uuid import uuid1
from PIL import Image
from mimetypes import guess_extension

from django.conf import settings

from rest_framework import status

from api.utils import smart_truncate
from sb_registration.utils import upload_image

"""
def crop_image(image, height, width, x, y, f_uuid=None):
    if f_uuid is None:
        f_uuid = str(uuid1())
    with Image.open(image) as image:
        src_width, src_height = image.size
        if src_width < width or src_height < height:
            image.thumbnail((height, width), Image.ANTIALIAS)
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            resized = image.resize((height, width), Image.ANTIALIAS)
            resized.save(image_name + ".png")
        else:
            region = image.crop((x, y, x + width, y + height))
            image_name = "%s-%sx%s" % (f_uuid, width, height)
            region.save(image_name + ".png")
        with open(image_name + ".png") as cropped_image:
            res = upload_image(settings.AWS_PROFILE_PICTURE_FOLDER_NAME,
                               image_name, cropped_image)
            if isinstance(res, Exception):
                return res
        os.remove(image_name + ".png")
    return res


def thumbnail_image(image, width, height, f_uuid=None):
    if f_uuid is None:
        f_uuid = str(uuid1())
    size = (width, height)
    image = Image.open(image)
    image.thumbnail(size, Image.ANTIALIAS)
    background = Image.new('RGBA', size, (255, 255, 255, 0))
    background.paste(image,
                     ((size[0] - image.size[0]) / 2, (size[1] -
                                                      image.size[1]) / 2))
    background.save(f_uuid + ".png")
"""


def resize_image(image, resize_width, resize_height):
    """
    This function will resize an image based upon the given width and height.
    If you use this to resize make sure you do any aspect ratio calculations
    before passing the values to this function as this does not attempt to
    maintain any aspect ratio.

    :param image:
    :param resize_width:
    :param resize_height:
    :return:
    """
    size = (int(float(resize_width)), int(float(resize_height)))
    resized = image.resize(size, Image.ANTIALIAS)
    return resized


def crop_image2(image, width, height, x, y):
    region = image.crop((x, y, x + width, y + height))
    return region


def is_absolute(url):
    return bool(urlparse.urlparse(url).netloc)


def get_page_image(url, soup, content_type='html/text'):
    height = 0
    width = 0
    image = soup.find(attrs={"property": "og:image"})
    if 'image' not in content_type:
        try:
            image = filter(lambda x: x in string.printable,
                           bleach.clean(image.get('content')))
        except AttributeError:
            images = soup.find_all('img')
            for test_url in images:
                if is_absolute(test_url['src']):
                    image = test_url['src']
                    break
            try:
                if image[:2] == "//":
                    image = image[2:]
                    if "http" not in image:
                        image = "http://" + image
            except (TypeError, AttributeError):
                return image, height, width
    else:
        image = url
    if 'image' in content_type or image:
        res = requests.get(image)
        if res.status_code == status.HTTP_200_OK:
            try:
                temp_file = cStringIO.StringIO(res.content)
            except IOError:  # pragma: no cover
                # this IOError catches issues created by passing StringIO some
                # corrupt or invalid data which we cannot test reliably
                # currently
                return "", height, width
            try:
                im = Image.open(temp_file)
                width, height = im.size
            except IOError:
                # this IOError handles the possibility of an SVG getting
                # passed here, PIL cannot open SVGs so the IOError handles that
                pass
            file_ext = guess_extension(res.headers['content-type'])
            image = upload_image(settings.AWS_UPLOAD_IMAGE_FOLDER_NAME,
                                 '%s%s' % (str(uuid1()), file_ext),
                                 temp_file, True)
        else:
            return "", height, width
    return image, height, width


def get_page_title(soup):
    html_parser = HTMLParser.HTMLParser()
    title = soup.find(attrs={"property": "og:title"})
    try:
        title = filter(lambda x: x in string.printable,
                       html_parser.unescape(
                           bleach.clean(title.get('content'))))
    except AttributeError:
        try:
            title = filter(
                lambda x: x in string.printable,
                html_parser.unescape(bleach.clean(
                    soup.find('title').string)))
        except AttributeError:
            pass
    return title


def get_page_description(soup):
    html_parser = HTMLParser.HTMLParser()
    description = soup.find(attrs={"property": "og:description"})
    try:
        description = smart_truncate(
            filter(lambda x: x in string.printable,
                   html_parser.unescape(bleach.clean(
                       description.get('content')))))
    except AttributeError:
        description = ""
    if description == "":
        try:
            description = smart_truncate(
                filter(lambda x: x in string.printable,
                       html_parser.unescape(bleach.clean(
                           soup.find(
                               attrs={"name": "description"}).get(
                               'content')))))
        except AttributeError:
            pass
    return description


def parse_page_html(soupified, url, content_type='html/text'):
    image, height, width = get_page_image(url, soupified, content_type)
    description = get_page_description(soupified)
    title = get_page_title(soupified)
    return title, description, image, width, height
