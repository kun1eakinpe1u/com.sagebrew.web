import pytz
from uuid import uuid1
from datetime import datetime
from api.utils import execute_cypher_query
from django.conf import settings
from django.template import Context
from django.template.loader import render_to_string, get_template

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,  BooleanProperty, FloatProperty,
                      CypherException)

from sb_base.neo_models import SBVersioned, SBTagContent
from sb_tag.neo_models import TagRelevanceModel
from sb_base.decorators import apply_defense


class SBQuestion(SBVersioned, SBTagContent):
    up_vote_adjustment = 5
    down_vote_adjustment = 2
    allowed_flags = ["explicit", "spam", "duplicate",
                     "unsupported", "other"]

    answer_number = IntegerProperty(default=0)
    question_title = StringProperty()
    is_closed = BooleanProperty(default=False)
    closed_reason = StringProperty()
    is_private = BooleanProperty()
    is_protected = BooleanProperty(default=False)
    is_mature = BooleanProperty(default=False)
    positivity = FloatProperty()
    subjectivity = FloatProperty()
    title_polarity = FloatProperty()
    title_subjectivity = FloatProperty()
    search_id = StringProperty()
    tags_added = BooleanProperty(default=False)
    added_to_search_index = BooleanProperty(default=False)

    # relationships
    tags = RelationshipTo('sb_tag.neo_models.SBTag', 'TAGGED_AS')
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    answer = RelationshipTo('sb_answers.neo_models.SBAnswer',
                            'POSSIBLE_ANSWER')

    @apply_defense
    def create_relations(self, pleb, question=None, wall=None):
        try:
            rel = self.owned_by.connect(pleb)
            rel.save()
            rel_from_pleb = pleb.questions.connect(self)
            rel_from_pleb.save()
            return True
        except CypherException as e:
            return e

    @apply_defense
    def edit_content(self, pleb, content):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(content, self.question_title,
                                                 str(uuid1()))

            if isinstance(edit_question, Exception) is True:
                return edit_question
            
            edit_question.original = False
            edit_question.save()
            self.edits.connect(edit_question)
            edit_question.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_question
        except (CypherException, AttributeError) as e:
            return e

    @apply_defense
    def edit_title(self, title):
        from sb_questions.utils import create_question_util
        try:
            edit_question = create_question_util(self.content, title,
                                                 str(uuid1()))

            if isinstance(edit_question, Exception) is True:
                return edit_question
            edit_question.original = False
            edit_question.save()
            self.edits.connect(edit_question)
            edit_question.edit_to.connect(self)
            self.last_edited_on = datetime.now(pytz.utc)
            self.save()
            return edit_question
        except CypherException as e:
            return e

    @apply_defense
    def delete_content(self, pleb):
        try:
            self.content = ""
            self.question_title = ""
            self.to_be_deleted = True
            self.save()
            return self
        except CypherException as e:
            return e

    @apply_defense
    def get_single_question_dict(self, pleb):
        from sb_answers.neo_models import SBAnswer
        try:
            answer_array = []
            owner = self.owned_by.all()
            owner = owner[0]
            owner_name = owner.first_name + ' ' + owner.last_name
            owner_profile_url = owner.username
            query = 'match (q:SBQuestion) where q.sb_id="%s" ' \
                    'with q ' \
                    'match (q)-[:POSSIBLE_ANSWER]-(a:SBAnswer) ' \
                    'where a.to_be_deleted=False ' \
                    'return a ' % self.sb_id
            answers, meta = execute_cypher_query(query)
            answers = [SBAnswer.inflate(row[0]) for row in answers]
            for answer in answers:
                answer_array.append(answer.get_single_answer_dict(pleb))
            edit = self.get_most_recent_edit()

            question_dict = {'question_title': edit.question_title,
                             'question_content': edit.content,
                             'question_uuid': self.sb_id,
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.get_upvote_count(),
                             'down_vote_number': self.get_downvote_count(),
                             'vote_score': self.get_vote_count(),
                             'owner': owner_name,
                             'owner_profile_url': owner_profile_url,
                             'time_created': self.date_created,
                             'answers': answer_array,
                             'current_pleb': pleb,
                             'owner_email': owner.email}
            return question_dict
        except CypherException as e:
            return e

    @apply_defense
    def get_multiple_question_dict(self, pleb):
        try:
            owner = self.owned_by.all()
            owner = owner[0]
            owner = owner.first_name + ' ' + owner.last_name
            question_dict = {'question_title': self.question_title,
                             'question_content': self.content[:50]+'...',
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.get_upvote_count(),
                             'down_vote_number': self.get_downvote_count(),
                             'vote_count': self.get_vote_count(),
                             'owner': owner,
                             'time_created': self.date_created,
                             # TODO Do we need the web address here?
                             'question_url': settings.WEB_ADDRESS +
                                             '/questions/' +
                                             self.sb_id,
                             'current_pleb': pleb
                        }
            return question_dict
        except CypherException as e:
            return e

    @apply_defense
    def render_question_page(self, pleb):
        try:
            owner = self.owned_by.all()
            try:
                owner = owner[0]
            except IndexError as e:
                # TODO Should we fail out here?
                return e
            owner = "%s %s" % (owner.first_name, owner.last_name)
            question_dict = {'question_title': self.
                                get_most_recent_edit().question_title,
                             'question_content':
                                 self.get_most_recent_edit().content[:50]+'...',
                             'is_closed': self.is_closed,
                             'answer_number': self.answer_number,
                             'last_edited_on': self.last_edited_on,
                             'up_vote_number': self.up_vote_number,
                             'down_vote_number': self.down_vote_number,
                             'owner': owner,
                             'time_created': self.date_created,
                             'question_url': self.sb_id,
                             'current_pleb': pleb
                        }
            t = get_template("questions.html")
            c = Context(question_dict)
            return t.render(c)
        except CypherException as e:
            return e

    @apply_defense
    def render_search(self):
        try:
            try:
                owner = self.owned_by.all()[0]
            except IndexError as e:
                return e
            owner_name = "%s %s" % (owner.first_name, owner.last_name)
            # TODO Do we need the WEB_ADDRESS can't we just use the absolute
            # path?
            owner_profile_url = owner.username
            question_dict = {
                "question_title": self.get_most_recent_edit().question_title,
                "question_content": self.get_most_recent_edit().content,
                "question_uuid": self.sb_id,
                "is_closed": self.is_closed,
                "answer_number": self.answer_number,
                "last_edited_on": self.last_edited_on,
                "up_vote_number": self.up_vote_number,
                "down_vote_number": self.down_vote_number,
                "owner": owner_name,
                "owner_profile_url": owner_profile_url,
                "time_created": self.date_created,
                "owner_email": owner.email}
            rendered = render_to_string('question_search.html', question_dict)
            return rendered
        except CypherException as e:
            return e

    @apply_defense
    def render_single(self, pleb):
        try:
            t = get_template("single_question.html")
            c = Context(self.get_single_question_dict(pleb))
            return t.render(c)
        except CypherException as e:
            return e

    def render_multiple(self, pleb):
        pass

    @apply_defense
    def get_original(self):
        try:
            if self.original is True:
                return self
            return self.edit_to.search(original=True)
        except CypherException as e:
            return e

    @apply_defense
    def get_most_recent_edit(self):
        try:
            results, columns = self.cypher('start q=node({self}) '
                                          'match q-[:EDIT]-(n:SBQuestion) '
                                          'with n '
                                          'ORDER BY n.date_created DESC return n')
            edits = [self.inflate(row[0]) for row in results]
            if not edits:
                return self
            return edits[0]
        except CypherException as e:
            return e