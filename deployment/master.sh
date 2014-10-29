#!/bin/sh

SHA1=$1
docker push sagebrew/sb_web:$SHA1
docker push sagebrew/sb_worker:$SHA1
EB_BUCKET=sagebrew-$CIRCLE_BRANCH
DOCKERRUN_FILE_WEB=$SHA1-master_Docker_web.aws.json
DOCKERRUN_FILE_WORKER=$SHA1-master_Docker_worker.aws.json
DOCKERRUN_WEB_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-master_Docker_web_environment.json
DOCKERRUN_WORKER_ENVIRONMENT=/home/ubuntu/com.sagebrew.web/$SHA1-master_Docker_worker_environment.json

sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_worker/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.worker_template > $DOCKERRUN_FILE_WORKER
sed "s/<TAG>/$SHA1/;s/<PROJECT_NAME>/$PROJECT_NAME/;s/<BUCKET>/$CIRCLE_BRANCH/;s/<IMAGE>/sb_web/;" < ~/com.sagebrew.web/aws_templates/Dockerrun.aws.json.web_template > $DOCKERRUN_FILE_WEB
~/virtualenvs/venv-system/bin/python ~/com.sagebrew.web/sagebrew/manage.py populateenvconfig $DOCKERRUN_WEB_ENVIRONMENT $DOCKERRUN_WORKER_ENVIRONMENT


aws s3 cp $DOCKERRUN_FILE_WEB s3://$EB_BUCKET/$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_WEB

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb
# Applications are the high level container that hold multiple environments such
# as a worker and a web instance.
# Need to look into if need version-label for both the first create application and the second
aws elasticbeanstalk create-application-version --application-name sagebrew-production-web \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKER_CONFIG_BUCKET/$DOCKERRUN_FILE_WEB --auto-create-application

aws elasticbeanstalk update-environment --option-settings file://$DOCKERRUN_WEB_ENVIRONMENT --environment-name sagebrew-production-web \
    --version-label $SHA1




aws s3 cp $DOCKERRUN_FILE_WORKER s3://$EB_BUCKET/$DOCKERRUN_FILE_WORKER

#/home/ubuntu/AWS-ElasticBeanstalk-CLI-2.6.3/eb/linux/python2.7/eb

aws elasticbeanstalk create-application-version --application-name sagebrew-production-worker \
  --version-label $SHA1 --source-bundle S3Bucket=$EB_BUCKET,S3Key=$DOCKERRUN_FILE_WORKER

aws elasticbeanstalk update-environment --option-settings $DOCKERRUN_WORKER_ENVIRONMENT --environment-name ssagebrew-production-worker \
    --version-label $SHA1