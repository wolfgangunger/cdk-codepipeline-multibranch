# cdk-feature-branch-codepipeline
cdk project with codepipeline to deploy aws resources to stage accounts  

it contains a pipeline to deploy from one branch to your stage accounts  
this pipeline is configured to deploy from one toolchain account to your stage accounts,   
so it is configured with cross account roles  

and a second pipeline to create pipelines for feature branches  
also cross account capable 


## project strucure
  
README  
github-actions-demo.yml (to be edited with your hook url)
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

## architecture
![image](https://github.com/wolfgangunger/cdk-codepipeline-multibranch/blob/main/feature-pipeline.jpg)
The project contains object orientated cdk design  
therefor cdk constructs are either in   
generic/infrastructure (reusable generic classes)  
or  
infrastructure (project specific classes)  


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
cdk bootstrap   --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess  aws://039735417706/eu-west-1

other accounts (dev, int , qa)
with stage credentials, first account is toolchain , second stage account
cdk bootstrap --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess --trust 12345678912 aws://12345678915/eu-west-1

###
commit your changes on cdk to your repo before deploying the pipeline

### deploy role(s)
cdk deploy bootstrap-dev-role-stack

### deploy the 'main' cdk pipeline via cli    (this pipeline will deploy the main/master branch, multi branch not supported)
cdk deploy  cdk-pipeline-multi-branch
    
now the pipeline should be ready and will be triggered on any push to the repo   
it will run immediatelly, so the stacks defined in this pipeline (in app_deploy and toolchain_deploy )will get deployed already   
this pipeline would also work stand alone, if you don't need the feature branch   
  
### deploy the feature-branch-pipeline-generator via cli    (this one generates for each branch a pipeline )
cdk deploy feature-branch-pipeline-generator

it will deploy the github webhook api and the pipeline template and the pipeline generator pipeline   

### edit secret ( if configured for git access )
Edit the secret github_webhook_secret to keep a structure like this:
{"SecretString" : "xxxxx"}

### edit github-actions-demo.yml
edit the webhook_url to your api gateway url ( or custom domain)  
change action triggers if needed   
otherwise your github cannot notify the api about a new branch  

### create branch and push to see the new feature pipeline gets generated
create a new branch  
git checkout -b feature/branch1  
and push to your repo  
the pipeline will be generated

### create PR and merge 
the pipeline will be destroyed  

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



