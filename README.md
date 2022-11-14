# cdk-codepipeline
cdk project with codepipeline to deploy aws resources to stage accounts

## project strucure
  
README  
cdk.json
requirements.txt  
app.py ( the main python file for the cdk commands, creates the Pipeline Stack)  
generic/infrastructure ( generic cdk classes and constructs to reuse in other projects)  
generic/infrastructure/tests ( cdk tests for this folder)  
infrastructure ( project specific cdk classes and constructs)  
infrastructure/tests ( cdk tests for this folder)  
infrastructure/lambdas/tests ( lambda tests)  
tests/acceptance  
tests/integration  

## setup project
###
create codestar connection in AWS Toolchain Account ( if you want to use code star. otherwise you have to configure your Github in the source )
### cdk.json
adapt the cdk.json for your accounts, also codestar connection url
adapt branch names etc
### write and add your stacks
create your own stacks and add to infrastructure folder, add to AppDeploy, write tests
### deploy the roles to the stage accounts
deploy the 3 roles to dev, qa and prod
for example with : cdk-deploy bootstrap-qa-role-stack
#### bootstrap
bootstrap the toolchain & stage accounts
with toolchain credentials
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://12345678912/us-east-1

other accounts (dev, int , qa)
with stage credentials, first account is toolchain , second stage account
cdk bootstrap --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess --trust 12345678912 aws://12345678915/eu-west-1



### deploy the pipeline via cli    
cdk deploy  cdk-pipeline  
and
cdk deploy cdk-pipeline-prod
  
now the pipeline should be ready and will be triggered on any push to the repo  

## tests
### infrastructure tests
pytest -vvvv -s generic/infrastructure/tests
pytest -vvvv -s infrastructure/tests
### lambda tests 
pytest -vvvv -s infrastructure/lambdas/tests
### integration tests
only dummy tests in this example 
### acceptance tests
only dummy tests in this example 


