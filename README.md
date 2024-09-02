##

## Deployment

1. Fork the repository.

2. Deploy the 1_base_infrastructure.yaml to your AWS account using Cloudformation. Add the Zero Knowledge prime and generator as parameters.

3. Add secrets for your AWS account and ECR Repository to Github Secrets.
AWS_ACCESS_KEY_ID=your AWS access key\
AWS_ACCOUNT_ID=your AWS account ID\
AWS_REGION=your aws region\
AWS_SECRET_ACCESS_KEY=your aws secret access key\
ECR_REPOSITORY_CLIENT=zkp_auth_client\
ECR_REPOSITORY_SERVER=zkp_auth_server

4. Run the Github Action workflow to trigger the Docker build and push to ECR.

5. Deploy the 2_high_availability_ecs.yaml to your AWS account using Cloudformation.