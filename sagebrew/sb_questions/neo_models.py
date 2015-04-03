import pytz
import markdown
from uuid import uuid1
from datetime import datetime
from api.utils import execute_cypher_query
from django.template import Context
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string, get_template

from neomodel import (StringProperty, IntegerProperty,
                      RelationshipTo,  BooleanProperty, FloatProperty,
                      CypherException)

from sb_base.neo_models import SBVersioned, SBTagContent
from sb_tag.neo_models import TagRelevanceModel
from sb_base.decorators import apply_defense


class SBQuestion(SBVersioned, SBTagContent):
    table = 'public_questions'
    action = "asked a question"
    up_vote_adjustment = 5
    down_vote_adjustment = 2
    object_type = "0274a216-644f-11e4-9ad9-080027242395"

    solution_count = IntegerProperty(default=0)
    title = StringProperty()
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
    auto_tags = RelationshipTo('sb_tag.neo_models.SBAutoTag',
                               'AUTO_TAGGED_AS', model=TagRelevanceModel)
    closed_by = RelationshipTo('plebs.neo_models.Pleb', 'CLOSED_BY')
    solutions = RelationshipTo('sb_solutions.neo_models.SBSolution',
                            'POSSIBLE_ANSWER')

    def get_url(self):
        return reverse("question_detail_page",
                       kwargs={"question_uuid": self.object_uuid})

    def create_notification(self, pleb, sb_object=None):
        return {
            "profile_pic": pleb.profile_pic,
            "full_name": pleb.get_full_name(),
            "action": self.action,
            "url": self.get_url()
        }

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
            edit_question = create_question_util(content, self.title,
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
            self.title = ""
            self.to_be_deleted = True
            self.save()
            return self
        except CypherException as e:
            return e

    @apply_defense
    def get_single_dict(self, pleb=None):
        from sb_solutions.neo_models import SBSolution
        try:
            solution_array = []
            comment_array = []
            owner = self.owned_by.all()
            try:
                owner = owner[0]
            except IndexError as e:
                return e
            # TODO is this used for storing solutions and comments
            # into dynamo? Or can we get rid of it and just return
            # the question specific data?
            query = 'match (q:SBQuestion) where q.object_uuid="%s" ' \
                    'with q ' \
                    'match (q)-[:POSSIBLE_ANSWER]-(a:SBSolution) ' \
                    'where a.to_be_deleted=False ' \
                    'return a ' % self.object_uuid
            solutions, meta = execute_cypher_query(query)
            solutions = [SBSolution.inflate(row[0]) for row in solutions]
            for solution in solutions:
                solution_array.append(solution.get_single_dict(pleb))
            edit = self.get_most_recent_edit()
            for comment in self.comments.all():
                comment_array.append(comment.get_single_dict())
            if self.content is None:
                html_content = ""
            else:
                html_content = markdown.markdown(self.content)
            return {
                'title': edit.title,
                'content': edit.content,
                'object_uuid': self.object_uuid,
                'is_closed': self.is_closed,
                'solution_count': self.solution_count,
                'last_edited_on': unicode(self.last_edited_on),
                'upvotes': self.get_upvote_count(),
                'downvotes': self.get_downvote_count(),
                'vote_count': self.get_vote_count(),
                'owner': owner.username,
                'owner_full_name': "%s %s" % (
                    owner.first_name, owner.last_name),
                'created': unicode(self.created),
                'solutions': solution_array,
                'comments': comment_array,
                'edits': [],
                'object_type': self.object_type,
                'to_be_deleted': self.to_be_deleted,
                'html_content': html_content}
        except (CypherException, IOError) as e:
            return e

    # TODO should be able to remove this and instead use the new endpoints
    @apply_defense
    def render_question_page(self, username):
        from sb_docstore.utils import get_vote
        try:
            owner = self.owned_by.all()
            try:
                owner = owner[0]
            except IndexError as e:
                return e
            owner = "%s %s" % (owner.first_name, owner.last_name)
            most_recent = self.get_most_recent_edit()
            if isinstance(most_recent, Exception):
                return most_recent
            if most_recent is not None:
                most_recent_content = most_recent.content
                if most_recent_content is not None:
                    vote_count = str(self.vote_count)
                    if vote_count == 'None':
                        vote_count = "0"
                    question_dict = {
                        'title': most_recent.title,
                        'question_content': most_recent_content,
                        'is_closed': self.is_closed,
                        'solution_count': self.solution_count,
                        'last_edited_on': self.last_edited_on,
                        'upvotes': self.upvotes,
                        'downvotes': self.downvotes,
                        'owner': owner,
                        'created': self.created,
                        'question_url': self.object_uuid,
                        'vote_count': vote_count
                    }
                    vote_type = get_vote(question_dict['question_url'],
                                         username)
                    if vote_type is not None:
                        if vote_type['status'] == 2:
                            vote_type = None
                        else:
                            vote_type = str(bool(vote_type['status'])).lower()
                    question_dict['vote_type'] = vote_type
                else:
                    question_dict = {"detail": "failed"}
            else:
                question_dict = {"detail": "failed"}
            t = get_template("question_summary.html")
            c = Context(question_dict)
            return t.render(c)
        except (CypherException, IOError) as e:
            return e

    @apply_defense
    def render_search(self):
        try:
            try:
                owner = self.owned_by.all()[0]
            except IndexError as e:
                return e
            owner_name = "%s %s" % (owner.first_name, owner.last_name)
            owner_profile_url = owner.username
            question_dict = {
                "title": self.get_most_recent_edit().title,
                "question_content": self.get_most_recent_edit().content,
                "object_uuid": self.object_uuid,
                "is_closed": self.is_closed,
                "solution_count": self.solution_count,
                "last_edited_on": self.last_edited_on,
                "upvotes": self.upvotes,
                "downvotes": self.downvotes,
                "vote_count": self.get_vote_count(),
                "owner": owner_name,
                "owner_profile_url": owner_profile_url,
                "created": self.created,
                "owner_email": owner.email,
                "views": len(self.view_count_node.all())}
            rendered = render_to_string('conversation_block.html', question_dict)
            return rendered
        except CypherException as e:
            return e

    def render_multiple(self, pleb):
        pass

    @apply_defense
    def render_single(self, pleb):
        try:
            t = get_template("question.html")
            c = Context(self.get_single_dict(pleb))
            return t.render(c)
        except CypherException as e:
            return e

    @apply_defense
    def get_original(self):
        try:
            if self.original is True:
                return self
            return self.edit_to.all()[0]
        except CypherException as e:
            return e

    @apply_defense
    def get_most_recent_edit(self):
        try:
            results, columns = self.cypher('start q=node({self}) '
                                           'match q-[:EDIT]-(n:SBQuestion) '
                                           'with n '
                                           'ORDER BY n.created DESC'
                                           ' return n')
            edits = [self.inflate(row[0]) for row in results]
            if not edits:
                return self
            return edits[0]
        except CypherException as e:
            return e