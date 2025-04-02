#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}

echo "Deploying Ghost Blog infrastructure for environment: $ENVIRONMENT"
echo "--------------------------------------------------------------"

STACKS=(
  "ghost-network:cloudformation/network.yaml"
  "ghost-rds:cloudformation/rds.yaml"
  "ghost-ecs:cloudformation/ecs.yaml"
  "ghost-alb:cloudformation/alb.yaml"
  "ghost-cloudfront:cloudformation/cloudfront.yaml"
  "ghost-ecs-service:cloudformation/ghost-ecs-service.yaml"
)

for stack in "${STACKS[@]}"; do
    IFS=":" read -r name template <<< "$stack"
    STACK_NAME="${ENVIRONMENT}-${name}"

    echo ""
    echo "▶ Deploying stack: $STACK_NAME"
    aws cloudformation deploy \
      --stack-name "$STACK_NAME" \
      --template-file "$template" \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides Environment=$ENVIRONMENT

    echo "⏳ Waiting for stack to finish: $STACK_NAME..."
    aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" || \
    aws cloudformation wait stack-update-complete --stack-name "$STACK_NAME"
    echo "✅ Stack completed: $STACK_NAME"
done

echo ""
echo "🚀 Deploying Lambda function via deploy-lambda.sh..."
./lambda/deploy-lambda.sh "$ENVIRONMENT"

echo ""
echo "✅ All stacks and Lambda deployed successfully!"
## ./deploy-all.sh dev
## For redeploying network template S3 bucket needs to be removed first  aws s3 rb s3://722208634435-dev-ghostblog-deleteposts-code --force
