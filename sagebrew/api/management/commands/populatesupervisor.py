import os
import logging
import multiprocessing
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger('loggly_logs')

class Command(BaseCommand):
    def populate_supervisor(self, env, user):
        worker_count = str((multiprocessing.cpu_count() *2) + 1)
        if(env == "web"):
            with open ("%s/supervisor_confs/web_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = data.replace("{{WEB_WORKER_COUNT}}", worker_count)
                data = data.replace("{{APP_USER}}", user)

            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        elif(env == "worker"):
            with open ("%s/supervisor_confs/worker_template.conf" % (
                    settings.REPO_DIR), "r") as dockerfile:
                data = dockerfile.read()
                data = data.replace("{{NUMBER_OF_WORKERS}}", worker_count)
                data = data.replace("{{APP_USER}}", user)
            f = open("/etc/supervisor/conf.d/sagebrew.conf", "w")
            f.write(data)
            f.close()
        else:
            pass

    def handle(self, *args, **options):
        self.populate_supervisor(args[0], args[1])