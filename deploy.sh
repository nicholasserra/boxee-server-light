#!/usr/bin/env bash

AWS_REGION="us-east-1"
DOCKER_IMAGE_NAME="boxee"

configure_aws_cli() {
    aws configure set default.region $AWS_REGION
}

push_docker_image() {
    if [ $# != 2 ] ; then
        echo "Aws_account_id, tag required."
        exit 1;
    fi

    local aws_account_id=${1}
    local tag=${2}

    docker build -t $DOCKER_IMAGE_NAME .

    # Push to ECR
    echo "Push to ECR"
    # Docker login for ECR
    eval $(aws ecr get-login --region $AWS_REGION --no-include-email)
    docker tag $DOCKER_IMAGE_NAME $aws_account_id.dkr.ecr.us-east-1.amazonaws.com/$DOCKER_IMAGE_NAME:$tag
    docker push $aws_account_id.dkr.ecr.us-east-1.amazonaws.com/$DOCKER_IMAGE_NAME:$tag
}

verify_account() {
    if [ $# != 1 ] ; then
        echo "AWS Account ID required"
        exit 1;
    fi

    local calling_account=$(aws sts get-caller-identity --output text --query 'Account')

    if [ $calling_account != $1 ]; then
        echo You are trying to deploy via incorrect credentials;
        exit 1;
    fi
}

update_service() {
    if [ $# != 3 ] ; then
        echo "Cluster name, service name, task definition revision arn required"
        exit 1;
    fi

    deployed_arn=$(aws ecs update-service --cluster $1 --service $2 --task-definition $3 --query 'service.taskDefinition' --output text)
    if [ $deployed_arn != $3 ] ; then
        echo "Error deploying cluster"
        exit 1;
    fi
}

register_task_definition() {
    if [ $# != 2 ] ; then
        echo "Required arguments missing."
        exit 1;
    fi

    local task_json=${1}
    local task_name=${2}

    revision_arn=$(aws ecs register-task-definition --container-definitions "$task_json" --family $task_name --query 'taskDefinition.taskDefinitionArn' --output text)

    echo $revision_arn
}

web_task_definition_json() {
    if [ $# != 9 ] ; then
        echo "Required arguments missing."
        exit 1;
    fi

    local task_name=${1}
    local image_tag=${2}
    local log_group_name=${3}
    local log_stream_prefix=${4}
    local memory=${5}
    local aws_account_id=${6}
    local database_url=${7}
    local stats_user=${8}
    local stats_pass=${9}

    local template='[
        {
            "name": "%s",
            "image": "%s.dkr.ecr.us-east-1.amazonaws.com/%s:%s",
            "essential": true,
            "memory": %s,
            "logConfiguration": {
                "logDriver": "awslogs",
                    "options": {
                       "awslogs-group": "%s",
                       "awslogs-region": "us-east-1",
                       "awslogs-stream-prefix": "%s"
                    }
            },
            "portMappings": [
                {
                    "hostPort": 80,
                    "protocol": "tcp",
                    "containerPort": 80
                }
            ],
            "environment": [
                {
                    "name": "ENVIRONMENT",
                    "value": "production"
                },
                {
                    "name": "TRACK_REQUESTS",
                    "value": "True"
                },
                {
                    "name": "DATABASE_URL",
                    "value": "%s"
                },
                {
                    "name": "STATS_USER",
                    "value": "%s"
                },
                {
                    "name": "STATS_PASS",
                    "value": "%s"
                }
            ]
        }
    ]'

    echo $(printf "$template" $task_name $aws_account_id $DOCKER_IMAGE_NAME $image_tag $memory $log_group_name $log_stream_prefix $database_url $stats_user $stats_pass)
}

deploy_environment() {
    if [ $# != 6 ] ; then
        echo "Arguments required."
        exit 1;
    fi

    local environment=$1
    local tag=$2
    local aws_account_id=$3
    local database_url=$4
    local stats_user=$5
    local stats_pass=$6

    # Environment input valid?
    if [[ "$environment" =~ ^(production)$ ]]; then
        echo Deploy $environment environment;
    else
        echo Invalid environment specified;
        exit 1;
    fi

    # Verify on correct AWS account
    if [[ "$environment" =~ ^(production)$ ]]; then
        verify_account $aws_account_id;
    fi

    if [ $environment == production ] ; then
        local api_task_definition_name="boxee"
        local api_service_name="boxee"
        local api_logs_stream_prefix="ecs"
        local cluster_name="boxee"
        local logs_group="/ecs/boxee"
        local memory=400
    fi

    echo "Deploy web" $environment $tag

    echo "Build web task definition json for updated image"
    local web_task_definition_json=$(web_task_definition_json $api_task_definition_name $tag $logs_group $api_logs_stream_prefix $memory $aws_account_id $database_url $stats_user $stats_pass)

    echo "Register new web task revision with updated task details"
    local revision_arn=$(register_task_definition "$web_task_definition_json" $api_task_definition_name)

    echo "Deploy new web task revision to service"
    update_service $cluster_name $api_service_name $revision_arn

    echo "Deploy web OK"
}

"$@"
