## Zero Knowledge Authentication

This is a basic implementation of zero knowledge authentication in Python. It includes everything needed to deploy a high availability server and client to production-grade infrastructure in AWS.

## Github Actions Workflow

This workflow will now automatically build and push your Docker images to Amazon ECR whenever there is a push to the main branch.

## CI

Tests are run automatically from all files prefixed with ```test_```. The tests are built into the Github Actions workflow and will fail if any tests fail.

## High Availability ECS

The infrastructure as code in the ```cloudformation``` folder will deploy a complete HA environment with two server instances as ECS tasks running on Fargate containers behind an internet-facing network load balancer and firewall. It will also deploy a client container that will authenticate with the server. Everything logs to Cloudwatch Logs, so you can see the interaction. 

## Deployment

1. Fork the repository.

2. Deploy the 1_base_infrastructure.yaml to your AWS account using Cloudformation via the console or cli. Add the zero knowledge prime and generator as parameters when deploying the Cloudformation template.

3. Add secrets for your AWS account and ECR Repository to Github Secrets.\
AWS_ACCESS_KEY_ID=your AWS access key\
AWS_ACCOUNT_ID=your AWS account ID\
AWS_REGION=your aws region\
AWS_SECRET_ACCESS_KEY=your aws secret access key\
ECR_REPOSITORY_CLIENT=zkp_auth_client\
ECR_REPOSITORY_SERVER=zkp_auth_server

4. Run the Github Action workflow to trigger the Docker build and push to ECR.

5. Deploy the 2_high_availability_ecs.yaml to your AWS account using Cloudformation.

## Deploying Code Updates

The Github Action workflow triggers on all pushes to main. This will run the tests, build the docker container and push to ECR with the tag ```latest```. To update the ECS tasks to run the latest code, update the ECS Service in the AWS console or via the cli to get the latest docker container from ECR.

## Improvements

There are a number of things that could be done to improve this project:

1. Further harden security by eliminating all wildcards in the IAM resource definitions.
2. Implement CD if desired.  
3. The Fargate containers are currently set up with a public IP for testing. This could be removed for security.
4. ECS tasks could communicate with each other over a private network for improved security.