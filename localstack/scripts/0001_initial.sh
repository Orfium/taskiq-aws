#!/usr/bin/env bash
# The script pre-configures the SNS and SQS queues and their subscriptions.

# enable debug
sleep 5;

chmod 755 /etc/localstack/init/ready.d/0001_initial.sh

echo "Creating development stack..."
awslocal \
    cloudformation deploy --stack-name stack \
    --template-file /etc/localstack/init/ready.d/localstack-cf.yml \
    --region ${AWS_REGION}
echo "Stack created successfully."