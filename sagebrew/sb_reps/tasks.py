from celery import shared_task

from .utils import (save_policy, save_experience, save_education, save_bio,
                    save_goal)


@shared_task()
def save_policy_task(rep_id, category, description, object_uuid):
    res1 = save_policy(rep_id, category, description, object_uuid)
    if isinstance(res1, Exception):
        raise save_policy_task.retry(exc=res1, countdown=3, max_retries=None)
    task_data = {
        'table': 'policies',
        'object_data': {'parent_object': rep_id, 'object_uuid': object_uuid,
                        'category': category, 'description': description}
    }
    return True

@shared_task()
def save_experience_task(rep_id, title, start_date, end_date, current,
                         company, location, exp_id, description=""):
    experience = save_experience(rep_id, title, start_date, end_date, current,
                                 company, location, exp_id, description)
    if isinstance(experience, Exception):
        raise save_experience_task.retry(exc=experience, countdown=3,
                                         max_retries=None)
    return True

@shared_task()
def save_education_task(rep_id, school, start_date, end_date, degree, edu_id):
    education = save_education(rep_id, school, start_date, end_date, degree,
                               edu_id)
    if isinstance(education, Exception):
        raise save_education_task.retry(exc=education, countdown=3,
                                        max_retries=None)
    return True

@shared_task()
def save_bio_task(rep_id, bio):
    bio = save_bio(rep_id, bio)
    if isinstance(bio, Exception):
        raise save_bio_task.retry(exc=bio, countdown=3, max_retries=None)
    return True

@shared_task()
def save_goal_task(rep_id, vote_req, money_req, initial, description, goal_id):
    goal = save_goal(rep_id, vote_req, money_req, initial, description,
                     goal_id)
    if isinstance(goal, Exception):
        raise save_goal_task.retry(exc=goal, countdown=3, max_retries=None)
    return True