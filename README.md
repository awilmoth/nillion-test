## Zero Knowledge Auth

This is a basic implementation of zero knowledge authentication in Python. It includes everything needed to deploy production-grade infrastructure in AWS.\

## Workflow

This workflow will now automatically build and push your Docker images to Amazon ECR whenever there is a push to the main branch.

## Deployment

1. Fork the repository.

2. Deploy the 1_base_infrastructure.yaml to your AWS account using Cloudformation. Add the Zero Knowledge prime and generator as parameters.

3. Add secrets for your AWS account and ECR Repository to Github Secrets.\
AWS_ACCESS_KEY_ID=your AWS access key\
AWS_ACCOUNT_ID=your AWS account ID\
AWS_REGION=your aws region\
AWS_SECRET_ACCESS_KEY=your aws secret access key\
ECR_REPOSITORY_CLIENT=zkp_auth_client\
ECR_REPOSITORY_SERVER=zkp_auth_server

4. Run the Github Action workflow to trigger the Docker build and push to ECR.

5. Deploy the 2_high_availability_ecs.yaml to your AWS account using Cloudformation.

## Updates

The Github Action workflow triggers on all pushes to main. This will run the tests, build the docker container and push to ECR with the tag ```latest```. To update the ECS tasks, update the ECS Deployment in the AWS console or via the cli to get the latest docker container from ECR.