import unicodedata as ud
import requests
from bs4 import BeautifulSoup

from time import sleep
from logging import getLogger
from dateutil import parser
from difflib import SequenceMatcher

from django.conf import settings

from neomodel import DoesNotExist, db

from .neo_models import NewsArticle

logger = getLogger("loggly_logs")


def is_latin(uchr):
    latin_letters = {}
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())


def find_news(limit_offset_fxn, count_query, link_objects_callback):
    requests_left = 26
    skip = 0
    limit = 25
    res, _ = db.cypher_query(count_query)
    total = res.one
    while requests_left > limit:
        news_objects = limit_offset_fxn(skip, limit)
        link_objects_callback(news_objects)
        if skip >= total:
            break
        skip += limit
        sleep(5)
    return True


def query_webhose(query):
    articles = []
    payload = {
        "token": settings.WEBHOSE_KEY,
        "format": "json",
        "q": query,
    }
    query = "https://webhose.io/search"
    response = requests.get(query, params=payload,
                            headers={"Accept": "text/plain"},
                            timeout=60)
    try:
        results = response.json()
    except ValueError as exc:
        logger.exception(exc)
        logger.critical(response.text)
        return None
    for post in results['posts']:
        if only_roman_chars(post['title']):
            thread = post.pop('thread', None)
            highlight_text = post.pop('highlightText', None)
            highlight_title = post.pop('highlightTitle', None)
            external_id = post.pop('uuid', None)
            content = post.pop('text', None)
            post.pop('ord_in_thread', None)
            thread.pop('published', None)
            crawled = parser.parse(post.pop('crawled', None))
            published = parser.parse(post.pop('published', None))
            url = post.pop('url', None)
            if settings.WEBHOSE_FREE:
                intermediate_page = requests.get(url)
                soup = BeautifulSoup(intermediate_page.text)
                for script in soup.find_all('script'):
                    index_value = str(script).find('window.location.href')
                    chop_string = str(script)[
                                  index_value+len('window.location.href="'):]
                    url = str(chop_string)[:chop_string.find('"')]
            if thread['spam_score'] < 0.5:
                try:
                    NewsArticle.nodes.get(external_id=external_id)
                except (NewsArticle.DoesNotExist, DoesNotExist):
                    # Get news articles with close titles, exact titles, or
                    # the same main image
                    query = 'MATCH (news:NewsArticle) ' \
                            'WHERE (news.title =~ "(?i).*%s.*" ) OR ' \
                            'news.title = "%s" OR news.main_image = "%s" ' \
                            'RETURN news' % (post['title'], post['title'],
                                             thread['main_image'])
                    res, _ = db.cypher_query(query)
                    for row in res:
                        # Check how close the titles are together
                        title_closeness = SequenceMatcher(
                            a=row[0]['title'], b=post['title']).ratio()
                        # Check how close the content is to each other
                        content_closeness = SequenceMatcher(
                            a=row[0]['content'], b=content).ratio()
                        if title_closeness > 0.83 or content_closeness > 0.85:
                            break
                        # See if they share an image
                        if row[0]['main_image'] == thread['main_image']:
                            # If they share the same image could still be
                            # different stories but since we don't want to show
                            # the same image twice on a feed lets be more strict
                            # on how different they need to be
                            if title_closeness > 0.65 or \
                                    content_closeness > 0.65:
                                break
                    else:
                        # If we get through the for loop without finding an
                        # article too similar to the proposed article then
                        # lets save it off
                        embedly_query = {
                            "url": url,
                            "key": settings.EMBEDLY_KEY,
                            'type': 'card'
                        }
                        embedly_res = requests.get(
                            'https://api.embedly.com/1/oembed',
                            params=embedly_query)
                        try:
                            embedly_json = embedly_res.json()
                            logger.critical(embedly_json)
                            rendered_content = embedly_json['html']
                            img_width = embedly_json['width']
                            img_height = embedly_json['height']
                            thumbnail_url = embedly_json['thumbnail_url']
                            thumbnail_width = embedly_json['thumbnail_width']
                            thumbnail_height = embedly_json['thumbnail_height']
                            description = embedly_json['description']
                            media_type = embedly_json['type']
                        except ValueError as exc:
                            logger.exception(exc)
                            logger.critical(response.text)
                            rendered_content = None
                        article = NewsArticle(
                            external_id=external_id,
                            url=url,
                            highlight_text=highlight_text,
                            highlight_title=highlight_title,
                            content=content, site_full=thread['site_full'],
                            site=thread['site'],
                            site_section=['site_section'],
                            section_title=thread['section_title'],
                            replies_count=thread['replies_count'],
                            participants_count=thread['participants_count'],
                            site_type=thread['site_type'],
                            country=thread['country'],
                            spam_score=thread['spam_score'],
                            main_image=thread['main_image'],
                            performance_score=thread['performance_score'],
                            crawled=crawled, published=published,
                            rendered_content=rendered_content,
                            **post).save()
                        articles.append(article)
    return articles, results['requestsLeft']


def tag_callback(news_objects):
    for tag in news_objects:
        query = '"%s" language:(english) thread.country:US ' \
                'performance_score:>8 (site_type:news)' % tag.name
        articles, requests_left = query_webhose(query)
        [article.tags.connect(tag) for article in articles]
    return True