from json import loads
import sys
from subprocess import call
from time import sleep
from os import environ

from boto.beanstalk import layer1


def deployment(stalk, branch_key):
    sha_key = environ.get("CIRCLE_SHA1", "")
    bean_bucket = "sagebrew-%s" % environ.get("CIRCLE_BRANCH", "")

    sys_util_name = "sys-util"
    sys_util = "sb-%s-%s" % (branch_key, sys_util_name)

    create_sys_util_env(sys_util, sys_util_name, branch_key, stalk, sha_key,
                        bean_bucket)
    create_app_version_update_env(branch_key, stalk, sha_key, bean_bucket,
                                  "web", "sagebrew-%s-web" % branch_key,
                                  "sb-%s-web" % branch_key)
    create_app_version_update_env(branch_key, stalk, sha_key, bean_bucket,
                                  "worker", "sagebrew-%s-worker" % branch_key,
                                  "sb-%s-worker" % branch_key)

    if environ.get("AUTO_TERMINATE", "false") == "true":
        sleep(15)
        terminate_sys_util_env(sys_util, stalk)


def terminate_sys_util_env(sys_util, stalk):
    sys_env = stalk.terminate_environment(environment_name=sys_util)

    sys_env = sys_env['TerminateEnvironmentResponse'][
        'TerminateEnvironmentResult']
    while sys_env[u"Status"] != u"Terminated":
        sleep(30)
        sys_env = stalk.describe_environments(application_name=sys_util,
                                              environment_names=[sys_util,])
        sys_env_app = sys_env["DescribeEnvironmentsResponse"][
            "DescribeEnvironmentsResult"]["Environments"]
        sys_env = sys_env_app[0]
        for env in sys_env_app:
            if env["DateCreated"] > sys_env["DateCreated"]:
                sys_env = env
        print sys_env[u"Status"]

    return sys_env


def create_sys_util_env(sys_util, sys_util_name, branch_key, stalk, sha_key,
                        bean_bucket):
    bean_key = "%s/%s-%s_%s.aws.json" % (environ.get(
        "DOCKER_CONFIG_BUCKET", ""), sha_key, branch_key, sys_util_name)
    aws_env = "/home/ubuntu/%s/%s-%s_%s.json" % ("com.sagebrew.web",
                                                 sha_key, branch_key,
                                                 "sys_util")
    option_tuple = populate_options(aws_env)
    stalk.create_application_version(application_name=sys_util,
                                     version_label=sha_key,
                                     s3_bucket=bean_bucket,
                                     s3_key=bean_key)
    # Need to create a template by manually creating the env first then
    # save the conf, then destroy
    sys_env = stalk.create_environment(environment_name=sys_util,
                                       application_name=sys_util,
                                       version_label=sha_key,
                                       option_settings=option_tuple,
                                       tier_name="WebServer",
                                       template_name='sys-util-conf')
    sys_env = sys_env["CreateEnvironmentResponse"]["CreateEnvironmentResult"]
    while sys_env[u"Status"] != u"Ready":
        sleep(30)
        sys_env = stalk.describe_environments(application_name=sys_util,
                                              environment_names=[sys_util,])
        sys_env_app = sys_env["DescribeEnvironmentsResponse"][
            "DescribeEnvironmentsResult"]["Environments"]
        sys_env = sys_env_app[0]
        for env in sys_env_app:
            if env["DateCreated"] > sys_env["DateCreated"]:
                sys_env = env
        print sys_env[u"Status"]

    return sys_env


def create_app_version_update_env(branch_key, stalk, sha_key, bean_bucket,
                                  app_type, app_name, env_name):
    bean_key = "%s/%s-%s_%s.zip" % (environ.get(
        "DOCKER_CONFIG_BUCKET", ""), sha_key, branch_key, app_type)
    aws_env = "/home/ubuntu/%s/%s-%s-%s.json" % ("com.sagebrew.web",
                                                 sha_key, branch_key, app_type)
    option_tuple = populate_options(aws_env)
    stalk.create_application_version(application_name=app_name,
                                     version_label=sha_key,
                                     s3_bucket=bean_bucket,
                                     s3_key=bean_key)

    stalk_env = stalk.update_environment(option_settings=option_tuple,
                                         environment_name=env_name,
                                         version_label=sha_key)
    stalk_env = stalk_env['UpdateEnvironmentResponse'][
        'UpdateEnvironmentResult']
    while stalk_env[u"Status"] != u"Ready":
        sleep(30)
        stalk_env = stalk.describe_environments(application_name=app_name,
                                                environment_names=[env_name,])
        web_env_app = stalk_env["DescribeEnvironmentsResponse"][
            "DescribeEnvironmentsResult"]["Environments"]
        stalk_env = web_env_app[0]
        for env in web_env_app:
            if env["DateCreated"] > stalk_env["DateCreated"]:
                stalk_env = env
        print stalk_env[u"Status"]

    return stalk_env


def populate_options(web_env):
    with open(web_env, "r") as option_file:
        data = option_file.read()
        option_list = loads(data)
        option_tuple = []
        for item in option_list:
            option_tuple.append((item["Namespace"], item["OptionName"],
                                item["Value"]))

    return option_tuple


def staging_deploy():
    stalk = layer1.Layer1(
        aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID_STAGING", ""),
        aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY_STAGING", ""),
        api_version='2010-12-01')
    deployment(stalk, "staging")


def production_deploy():
    stalk = layer1.Layer1(
        aws_access_key_id=environ.get("AWS_ACCESS_KEY_ID_PROD", ""),
        aws_secret_access_key=environ.get("AWS_SECRET_ACCESS_KEY_PROD", ""),
        api_version='2010-12-01')
    deployment(stalk, "master")


if __name__ == "__main__":
    if sys.argv[1] == "staging":
        staging_deploy()
        call(
            'curl https://opbeat.com/api/v1/organizations/'
            '%s/apps/%s/releases/' % (environ.get(
                "OPBEAT_ORG_ID_STAGING", ""), environ.get(
                    "OPBEAT_APP_ID_STAGING", "")) +
            ' -H "Authorization: Bearer %s" ' % environ.get(
                "OPBEAT_SECRET_TOKEN_STAGING", "") +
            '-d rev=`git log -n 1 --pretty=format:%H` '
            '-d branch=`git rev-parse --abbrev-ref HEAD` '
            '-d status=completed', shell=True)
    elif sys.argv[1] == "master":
        production_deploy()
        call(
            'curl https://opbeat.com/api/v1/organizations/'
            '%s/apps/%s/releases/' % (environ.get(
                "OPBEAT_ORG_ID_PROD", ""), environ.get(
                    "OPBEAT_APP_ID_PROD", "")) +
            ' -H "Authorization: Bearer %s" ' % environ.get(
                "OPBEAT_SECRET_TOKEN_PROD", "") +
            '-d rev=`git log -n 1 --pretty=format:%H` '
            '-d branch=`git rev-parse --abbrev-ref HEAD` '
            '-d status=completed', shell=True)