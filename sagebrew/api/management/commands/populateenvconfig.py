from os import environ
import logging

from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('web_env', nargs='+', type=str)
        parser.add_argument('worker_env', nargs='+', type=str)

    def populate_config(self, web_env, worker_env):
        cur_branch = environ.get("CIRCLE_BRANCH", "")
        with open("%s/aws_environment_config/base.config" % (
                settings.REPO_DIR), "r") as dockerfile:
            data = dockerfile.read()
            if cur_branch == "staging":
                data = populate_staging_values(data)
            elif cur_branch == "master":
                data = populate_production_values(data)
            else:
                data = populate_test_values(data)
            data = populate_general_values(data)
        with open("%s/aws_environment_config/base_worker.config" % (
                settings.REPO_DIR), "r") as docker_worker:
            data_worker = docker_worker.read()
            if cur_branch == "staging":
                data_worker = populate_staging_values(data_worker)
            elif cur_branch == "master":
                data_worker = populate_production_values(data_worker)
            else:
                data_worker = populate_test_values(data_worker)
            data_worker = populate_general_values(data_worker)
        f = open("%s" % web_env, "w")
        f.write(data)
        f.close()
        f = open("%s" % worker_env, "w")
        f.write(data_worker)
        f.close()
        with open("%s/aws_environment_config/sys_util.config" % (
                settings.REPO_DIR), "r") as docker_sys:
            data_worker = docker_sys.read()
            if cur_branch == "staging":
                data_worker = populate_staging_values(data_worker)
            elif cur_branch == "master":
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
        self.populate_config(options['web_env'][0], options['worker_env'][0])


def populate_staging_values(data):
    data = data.replace("<NEO4J_REST_URL>",
                        environ.get("STAGING_NEO4J_REST_URL", ""))
    data = data.replace("<AWS_ACCESS_KEY_ID>",
                        environ.get("AWS_ACCESS_KEY_ID_STAGING", ""))
    data = data.replace("<AWS_S3_BUCKET>", environ.get("AWS_S3_BUCKET_STAGING",
                                                       ""))
    data = data.replace("<AWS_SECRET_ACCESS_KEY>",
                        environ.get("AWS_SECRET_ACCESS_KEY_STAGING", ""))
    data = data.replace("<APPLICATION_SECRET_KEY>",
                        environ.get("APPLICATION_SECRET_KEY_STAGING", ""))
    data = data.replace("<REDIS_LOCATION>",
                        environ.get("REDIS_LOCATION_STAGING", ""))
    data = data.replace("<CACHE_LOCATION>",
                        environ.get("CACHE_LOCATION_STAGING", ""))
    data = data.replace("<RDS_DB_NAME>",
                        environ.get("RDS_DB_NAME_STAGING", ""))
    data = data.replace("<RDS_USERNAME>",
                        environ.get("RDS_USERNAME_STAGING", ""))
    data = data.replace("<RDS_PASSWORD>",
                        environ.get("RDS_PASSWORD_STAGING", ""))
    data = data.replace("<RDS_HOSTNAME>",
                        environ.get("RDS_HOSTNAME_STAGING", ""))
    data = data.replace("<WEB_SECURITY_GROUP>",
                        environ.get("WEB_SECURITY_GROUP_STAGING", ""))
    data = data.replace("<STRIPE_PUBLIC_KEY>",
                        environ.get("STRIPE_PUBLIC_KEY", ""))
    data = data.replace("<STRIPE_SECRET_KEY>",
                        environ.get("STRIPE_SECRET_KEY", ""))
    data = data.replace("<MASKED_NAME>",
                        environ.get("MASKED_NAME_STAGING", ""))
    data = data.replace("<OPBEAT_ORG_ID>",
                        environ.get("OPBEAT_ORG_ID_STAGING", ""))
    data = data.replace("<OPBEAT_APP_ID>",
                        environ.get("OPBEAT_APP_ID_STAGING", ""))
    data = data.replace("<OPBEAT_SECRET_TOKEN>",
                        environ.get("OPBEAT_SECRET_TOKEN_STAGING", ""))
    data = data.replace("<LOGENT_TOKEN>",
                        environ.get("LOGENT_TOKEN_STAGING", ""))
    data = data.replace("<SYS_LOG_TOKEN>",
                        environ.get("SYS_LOG_TOKEN_STAGING", ""))
    data = data.replace("<OAUTH_CLIENT_ID>",
                        environ.get("OAUTH_CLIENT_ID_STAGING", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET>",
                        environ.get("OAUTH_CLIENT_SECRET_STAGING", ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED>",
                        environ.get("OAUTH_CLIENT_ID_CRED_STAGING", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_STAGING", ""))
    data = data.replace("<CRED_USER>", environ.get("CRED_USER_STAGING", ""))
    data = data.replace("<CRED_PASSWORD>",
                        environ.get("CRED_PASSWORD_STAGING", ""))
    data = data.replace("<CRED_USER_PUBLIC>",
                        environ.get("CRED_USER_PUBLIC_STAGING", ""))
    data = data.replace("<CRED_PASSWORD_PUBLIC>",
                        environ.get("CRED_PASSWORD_PUBLIC_STAGING", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_PUBLIC_STAGING",
                                    ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_ID_CRED_PUBLIC_STAGING", ""))
    data = data.replace("<ELASTIC_SEARCH_HOST>",
                        environ.get("ELASTIC_SEARCH_HOST_STAGING", ""))
    data = data.replace("<ELASTIC_SEARCH_PORT>",
                        environ.get("ELASTIC_SEARCH_PORT_STAGING", ""))
    data = data.replace("<ELASTIC_SEARCH_USER>",
                        environ.get("ELASTIC_SEARCH_USER_STAGING", ""))
    data = data.replace("<ELASTIC_SEARCH_KEY>",
                        environ.get("ELASTIC_SEARCH_KEY_STAGING", ""))
    data = data.replace("<ADDRESS_VALIDATION_ID>",
                        environ.get("ADDRESS_VALIDATION_ID_STAGING", ""))
    data = data.replace("<ADDRESS_VALIDATION_TOKEN>",
                        environ.get("ADDRESS_VALIDATION_TOKEN_STAGING", ""))
    data = data.replace("<ADDRESS_AUTH_ID>",
                        environ.get("ADDRESS_AUTH_ID_STAGING", ""))
    data = data.replace("<GOOGLE_MAPS_API>",
                        environ.get("GOOGLE_MAPS_API_STAGING", ""))
    data = data.replace("<GOOGLE_MAPS_JS>",
                        environ.get("GOOGLE_MAPS_JS_STAGING", ""))
    data = data.replace("<INTERCOM_API_KEY>",
                        environ.get("INTERCOM_API_KEY_STAGING", ""))
    data = data.replace("<INTERCOM_APP_ID>",
                        environ.get("INTERCOM_APP_ID_STAGING", ""))
    data = data.replace("<INTERCOM_ADMIN_ID_DEVON>",
                        environ.get("INTERCOM_ADMIN_ID_DEVON_STAGING", ""))
    return data


def populate_production_values(data):
    data = data.replace("<NEO4J_REST_URL>",
                        environ.get("NEO4J_REST_URL_PROD", ""))
    data = data.replace("<AWS_ACCESS_KEY_ID>",
                        environ.get("AWS_ACCESS_KEY_ID_PROD", ""))
    data = data.replace("<AWS_S3_BUCKET>",
                        environ.get("AWS_S3_BUCKET_PROD", ""))
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
    data = data.replace("<WEB_SECURITY_GROUP>",
                        environ.get("WEB_SECURITY_GROUP_PROD", ""))
    data = data.replace("<STRIPE_PUBLIC_KEY>",
                        environ.get("STRIPE_PUBLIC_KEY_PROD", ""))
    data = data.replace("<STRIPE_SECRET_KEY>",
                        environ.get("STRIPE_SECRET_KEY_PROD", ""))
    data = data.replace("<MASKED_NAME>",
                        environ.get("MASKED_NAME_PROD", ""))
    data = data.replace("<LOGENT_TOKEN>",
                        environ.get("LOGENT_TOKEN_PROD", ""))
    data = data.replace("<SYS_LOG_TOKEN>",
                        environ.get("SYS_LOG_TOKEN_PROD", ""))
    data = data.replace("<OPBEAT_ORG_ID>",
                        environ.get("OPBEAT_ORG_ID_PROD", ""))
    data = data.replace("<OPBEAT_APP_ID>",
                        environ.get("OPBEAT_APP_ID_PROD", ""))
    data = data.replace("<OPBEAT_SECRET_TOKEN>",
                        environ.get("OPBEAT_SECRET_TOKEN_PROD", ""))
    data = data.replace("<OAUTH_CLIENT_ID>",
                        environ.get("OAUTH_CLIENT_ID_PROD", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET>",
                        environ.get("OAUTH_CLIENT_SECRET_PROD", ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED>",
                        environ.get("OAUTH_CLIENT_ID_CRED_PROD", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_PROD", ""))
    data = data.replace("<CRED_USER>", environ.get("CRED_USER_PROD", ""))
    data = data.replace("<CRED_PASSWORD>",
                        environ.get("CRED_PASSWORD_PROD", ""))
    data = data.replace("<CRED_USER_PUBLIC>",
                        environ.get("CRED_USER_PUBLIC_PROD", ""))
    data = data.replace("<CRED_PASSWORD_PUBLIC>",
                        environ.get("CRED_PASSWORD_PUBLIC_PROD", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_PUBLIC_PROD",
                                    ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_ID_CRED_PUBLIC_PROD", ""))
    data = data.replace("<ELASTIC_SEARCH_HOST>",
                        environ.get("ELASTIC_SEARCH_HOST_PROD", ""))
    data = data.replace("<ELASTIC_SEARCH_PORT>",
                        environ.get("ELASTIC_SEARCH_PORT_PROD", ""))
    data = data.replace("<ELASTIC_SEARCH_USER>",
                        environ.get("ELASTIC_SEARCH_USER_PROD", ""))
    data = data.replace("<ELASTIC_SEARCH_KEY>",
                        environ.get("ELASTIC_SEARCH_KEY_PROD", ""))
    data = data.replace("<ADDRESS_VALIDATION_ID>",
                        environ.get("ADDRESS_VALIDATION_ID_PROD", ""))
    data = data.replace("<ADDRESS_VALIDATION_TOKEN>",
                        environ.get("ADDRESS_VALIDATION_TOKEN_PROD", ""))
    data = data.replace("<ADDRESS_AUTH_ID>",
                        environ.get("ADDRESS_AUTH_ID_PROD", ""))
    data = data.replace("<GOOGLE_MAPS_API>",
                        environ.get("GOOGLE_MAPS_API_PROD", ""))
    data = data.replace("<GOOGLE_MAPS_JS>",
                        environ.get("GOOGLE_MAPS_JS_PROD", ""))
    data = data.replace("<INTERCOM_API_KEY>",
                        environ.get("INTERCOM_API_KEY_PROD", ""))
    data = data.replace("<INTERCOM_APP_ID>",
                        environ.get("INTERCOM_APP_ID_PROD", ""))
    data = data.replace("<INTERCOM_ADMIN_ID_DEVON>",
                        environ.get("INTERCOM_ADMIN_ID_DEVON_PROD", ""))
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
    data = data.replace("<STRIPE_PUBLIC_KEY>",
                        environ.get("STRIPE_PUBLIC_KEY", ""))
    data = data.replace("<STRIPE_SECRET_KEY>",
                        environ.get("STRIPE_SECRET_KEY", ""))
    data = data.replace("<MASKED_NAME>",
                        environ.get("MASKED_NAME", ""))
    data = data.replace("<LOGENT_TOKEN>", environ.get("LOGENT_TOKEN", ""))
    data = data.replace("<SYS_LOG_TOKEN>", environ.get("SYS_LOG_TOKEN", ""))
    data = data.replace("<OAUTH_CLIENT_ID>",
                        environ.get("OAUTH_CLIENT_ID", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET>",
                        environ.get("OAUTH_CLIENT_SECRET", ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED>",
                        environ.get("OAUTH_CLIENT_ID_CRED", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED", ""))
    data = data.replace("<CRED_USER>", environ.get("CRED_USER", ""))
    data = data.replace("<CRED_PASSWORD>",
                        environ.get("CRED_PASSWORD", ""))
    data = data.replace("<CRED_USER_PUBLIC>",
                        environ.get("CRED_USER_PUBLIC", ""))
    data = data.replace("<CRED_PASSWORD_PUBLIC>",
                        environ.get("CRED_PASSWORD_PUBLIC", ""))
    data = data.replace("<OAUTH_CLIENT_SECRET_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_SECRET_CRED_PUBLIC",
                                    ""))
    data = data.replace("<OAUTH_CLIENT_ID_CRED_PUBLIC>",
                        environ.get("OAUTH_CLIENT_ID_CRED_PUBLIC", ""))
    data = data.replace("<ELASTIC_SEARCH_HOST>",
                        environ.get("ELASTIC_SEARCH_HOST", ""))
    data = data.replace("<ELASTIC_SEARCH_PORT>",
                        environ.get("ELASTIC_SEARCH_PORT", ""))
    data = data.replace("<ELASTIC_SEARCH_USER>",
                        environ.get("ELASTIC_SEARCH_USER", ""))
    data = data.replace("<ELASTIC_SEARCH_KEY>",
                        environ.get("ELASTIC_SEARCH_KEY", ""))
    data = data.replace("<ADDRESS_VALIDATION_ID>",
                        environ.get("ADDRESS_VALIDATION_ID", ""))
    data = data.replace("<ADDRESS_VALIDATION_TOKEN>",
                        environ.get("ADDRESS_VALIDATION_TOKEN", ""))
    data = data.replace("<ADDRESS_AUTH_ID>",
                        environ.get("ADDRESS_AUTH_ID", ""))
    data = data.replace("<GOOGLE_MAPS_API>",
                        environ.get("GOOGLE_MAPS_API", ""))
    data = data.replace("<GOOGLE_MAPS_JS>",
                        environ.get("GOOGLE_MAPS_JS", ""))
    data = data.replace("<INTERCOM_API_KEY>",
                        environ.get("INTERCOM_API_KEY_STAGING", ""))
    data = data.replace("<INTERCOM_APP_ID>",
                        environ.get("INTERCOM_APP_ID_STAGING", ""))
    data = data.replace("<INTERCOM_ADMIN_ID_DEVON>",
                        environ.get("INTERCOM_ADMIN_ID_DEVON_STAGING", ""))
    return data


def populate_general_values(data):
    data = data.replace("<RDS_PORT>",
                        environ.get("RDS_PORT", ""))
    data = data.replace("<SHA1>", environ.get("CIRCLE_SHA1", ""))
    data = data.replace("<APP_USER>", environ.get("APP_USER", ""))
    data = data.replace("<APP_NAME>", environ.get("APP_NAME", ""))
    data = data.replace("<PROJECT_REPONAME>",
                        environ.get("PROJECT_REPONAME",
                                    environ.get("CIRCLE_PROJECT_REPONAME", "")))
    data = data.replace("<PROJECT_NAME>", environ.get("PROJECT_NAME"))

    data = data.replace("<CIRCLE_BRANCH>", environ.get("CIRCLE_BRANCH", ""))

    data = data.replace("<BOMBERMAN_API_KEY>",
                        environ.get("BOMBERMAN_API_KEY", ""))
    data = data.replace("<SSL_CERT_LOCATION>",
                        environ.get("SSL_CERT_LOCATION", ""))
    data = data.replace("<SSL_KEY_LOCATION>",
                        environ.get("SSL_KEY_LOCATION", ""))

    data = data.replace("<ALCHEMY_API_KEY>",
                        environ.get("ALCHEMY_API_KEY", ""))

    data = data.replace("<REDIS_PORT>", environ.get("REDIS_PORT", ""))
    data = data.replace("<QUEUE_USERNAME>", environ.get("QUEUE_USERNAME", ""))
    data = data.replace("<QUEUE_PASSWORD>", environ.get("QUEUE_PASSWORD", ""))
    data = data.replace("<QUEUE_HOST>", environ.get("QUEUE_HOST", ""))
    data = data.replace("<QUEUE_PORT>", environ.get("QUEUE_PORT", ""))
    data = data.replace("<AWS_DEFAULT_REGION>",
                        environ.get("AWS_DEFAULT_REGION", ""))
    data = data.replace("<SUNLIGHT_FOUNDATION_KEY>",
                        environ.get("SUNLIGHT_FOUNDATION_KEY", ""))
    data = data.replace("<WEBHOSE_KEY>", environ.get("WEBHOSE_KEY", ""))
    return data
