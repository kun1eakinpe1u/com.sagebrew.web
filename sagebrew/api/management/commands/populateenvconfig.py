from os import environ
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')

class Command(BaseCommand):

    def populate_config(self, web_env, worker_env):
        cur_branch = environ.get("CIRCLE_BRANCH", "")
        with open("%s/aws_environment_config/base.config" % (
                settings.REPO_DIR), "r") as dockerfile:
            data = dockerfile.read()
            if(cur_branch == "staging"):
                data = populate_staging_values(data)
            elif(cur_branch == "master"):
                data = populate_production_values(data)
            else:
                data = populate_test_values(data)
            data = populate_general_values(data)
        with open("%s/aws_environment_config/base_worker.config" % (
            settings.REPO_DIR), "r") as docker_worker:
            data_worker = docker_worker.read()
            if(cur_branch == "staging"):
                data_worker = populate_staging_values(data_worker)
            elif(cur_branch == "master"):
                data_worker = populate_production_values(data_worker)
            else:
                data_worker = populate_test_values(data_worker)
            data_worker = populate_general_values(data_worker)
        f = open("%s" % (web_env), "w")
        f.write(data)
        f.close()
        f = open("%s" % (worker_env), "w")
        f.write(data_worker)
        f.close()
        with open("%s/aws_environment_config/sys_util.config" % (
            settings.REPO_DIR), "r") as docker_sys:
            data_worker = docker_sys.read()
            if(cur_branch == "staging"):
                data_worker = populate_staging_values(data_worker)
            elif(cur_branch == "master"):
                data_worker = populate_production_values(data_worker)
            else:
                data_worker = populate_test_values(data_worker)
            data_worker = populate_general_values(data_worker)
        sys_env = "/home/ubuntu/com.sagebrew.web/%s-%s_sys_util.json" % (
            environ.get("CIRCLE_SHA1", ""), environ.get("CIRCLE_BRANCH", "")
        )
        f = open(sys_env, "w")
        f.write(data_worker)
        f.close()


    def handle(self, *args, **options):
        self.populate_config(args[0], args[1])

def populate_staging_values(data):
    data = data.replace("<NEO4J_REST_URL>",
                             environ.get("STAGING_NEO4J_REST_URL", ""))
    data = data.replace("<AWS_ACCESS_KEY_ID>",
                        environ.get("AWS_ACCESS_KEY_ID_STAGING", ""))
    data = data.replace("<AWS_S3_BUCKET>", environ.get("AWS_S3_BUCKET_STAGING", ""))
    data = data.replace("<AWS_SECRET_ACCESS_KEY>",
                        environ.get("AWS_SECRET_ACCESS_KEY_STAGING", ""))
    data = data.replace("<APPLICATION_SECRET_KEY>",
                        environ.get("APPLICATION_SECRET_KEY_STAGING", ""))
    data = data.replace("<REDIS_LOCATION>",
                        environ.get("REDIS_LOCATION_STAGING", ""))
    data = data.replace("<CACHE_LOCATION>",
                        environ.get("CACHE_LOCATION_STAGING", ""))
    # Only populated in worker config (web gets these by default from aws)
    data = data.replace("<RDS_DB_NAME>",
                        environ.get("RDS_DB_NAME_STAGING", ""))
    data = data.replace("<RDS_USERNAME>",
                        environ.get("RDS_USERNAME_STAGING", ""))
    data = data.replace("<RDS_PASSWORD>",
                        environ.get("RDS_PASSWORD_STAGING", ""))
    data = data.replace("<RDS_HOSTNAME>",
                        environ.get("RDS_HOSTNAME_STAGING", ""))
    data = data.replace("<CELERY_QUEUE>",
                        environ.get("CELERY_QUEUE_STAGING", ""))
    data = data.replace("<WEB_SECURITY_GROUP>",
                        environ.get("WEB_SECURITY_GROUP_STAGING", ""))
    return data


def populate_production_values(data):
    data = data.replace("<NEO4J_REST_URL>",
                             environ.get("NEO4J_REST_URL_PROD", ""))
    data = data.replace("<AWS_ACCESS_KEY_ID>",
                        environ.get("AWS_ACCESS_KEY_ID_PROD", ""))
    data = data.replace("<AWS_S3_BUCKET>", environ.get("AWS_S3_BUCKET_PROD", ""))
    data = data.replace("<AWS_SECRET_ACCESS_KEY>",
                        environ.get("AWS_SECRET_ACCESS_KEY_PROD", ""))
    data = data.replace("<APPLICATION_SECRET_KEY>",
                        environ.get("APPLICATION_SECRET_KEY_PROD", ""))
    data = data.replace("<REDIS_LOCATION>",
                        environ.get("REDIS_LOCATION_PROD", ""))
    data = data.replace("<CACHE_LOCATION>",
                        environ.get("CACHE_LOCATION_PROD", ""))
    # Only populated in worker config (web gets these by default from aws)
    data = data.replace("<RDS_DB_NAME>",
                        environ.get("RDS_DB_NAME_PROD", ""))
    data = data.replace("<RDS_USERNAME>",
                        environ.get("RDS_USERNAME_PROD", ""))
    data = data.replace("<RDS_PASSWORD>",
                        environ.get("RDS_PASSWORD_PROD", ""))
    data = data.replace("<RDS_HOSTNAME>",
                        environ.get("RDS_HOSTNAME_PROD", ""))
    data = data.replace("<CELERY_QUEUE>",
                        environ.get("CELERY_QUEUE_PROD", ""))
    data = data.replace("<WEB_SECURITY_GROUP>",
                        environ.get("WEB_SECURITY_GROUP_PROD", ""))
    return data

def populate_test_values(data):
    data = data.replace("<NEO4J_REST_URL>",
                             environ.get("GRAPHEN_NEO4J_REST_URL", ""))
    data = data.replace("<AWS_ACCESS_KEY_ID>",
                        environ.get("AWS_ACCESS_KEY_ID", ""))
    data = data.replace("<AWS_S3_BUCKET>", environ.get("AWS_S3_BUCKET", ""))
    data = data.replace("<AWS_SECRET_ACCESS_KEY>",
                        environ.get("AWS_SECRET_ACCESS_KEY", ""))
    data = data.replace("<APPLICATION_SECRET_KEY>",
                        environ.get("APPLICATION_SECRET_KEY", ""))
    return data


def populate_general_values(data):
    data = data.replace("<RDS_PORT>",
                        environ.get("RDS_PORT", ""))
    data = data.replace("<APP_USER>", environ.get("APP_USER", ""))
    data = data.replace("<REPO_NAME>", environ.get("REPO_NAME", ""))
    data = data.replace("<PROJECT_NAME>", environ.get("PROJECT_NAME"))
    data = data.replace("<LOG_ACCOUNT>", environ.get("LOG_ACCOUNT", ""))
    data = data.replace("<LOG_TOKEN>", environ.get("LOG_TOKEN", ""))

    data = data.replace("<CIRCLE_BRANCH>", environ.get("CIRCLE_BRANCH", ""))

    data = data.replace("<BOMBERMAN_API_KEY>",
                        environ.get("BOMBERMAN_API_KEY", ""))
    data = data.replace("<SSL_CERT_LOCATION>",
                        environ.get("SSL_CERT_LOCATION", ""))
    data = data.replace("<SSL_KEY_LOCATION>",
                        environ.get("SSL_KEY_LOCATION", ""))

    data = data.replace("<ALCHEMY_API_KEY>",
                        environ.get("ALCHEMY_API_KEY", ""))
    data = data.replace("<ADDRESS_VALIDATION_ID>",
                        environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("<ADDRESS_VALIDATION_TOKEN>",
                        environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("<ELASTIC_SEARCH_HOST>",
                        environ.get("ELASTIC_SEARCH_HOST", ""))
    data = data.replace("<ELASTIC_SEARCH_PORT>",
                        environ.get("ELASTIC_SEARCH_PORT", ""))
    data = data.replace("<ELASTIC_SEARCH_USER>",
                        environ.get("ELASTIC_SEARCH_USER", ""))
    data = data.replace("<ELASTIC_SEARCH_KEY>",
                        environ.get("ELASTIC_SEARCH_KEY", ""))

    data = data.replace("<REDIS_PORT>", environ.get("REDIS_PORT", ""))
    data = data.replace("<QUEUE_USERNAME>", environ.get("QUEUE_USERNAME", ""))
    data = data.replace("<QUEUE_PASSWORD>", environ.get("QUEUE_PASSWORD", ""))
    data = data.replace("<QUEUE_HOST>", environ.get("QUEUE_HOST", ""))
    data = data.replace("<QUEUE_PORT>", environ.get("QUEUE_PORT", ""))

    return data