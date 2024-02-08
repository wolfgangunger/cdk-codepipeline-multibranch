# cdk-feature-branch-codepipeline
cdk project with codepipeline to deploy aws resources to stage accounts  

it contains a pipeline to deploy from one branch to your stage accounts  
this pipeline is configured to deploy from one toolchain account to your stage accounts,   
so it is configured with cross account roles  

and a second pipeline to create pipelines for feature branches  
also cross account capable 

if you want to test this pipeline in just one account, please define in cdk.json the 4 accounts with the same number  
this works, but keep in mind, you should not deploy twice in the same account.  
for example the dev/qa pipeline would deploy to 2 accounts. don't confirm the manual approval before QA in this case.  


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
### clone this repo to your own git repo
clone this repo to your own git repo
the pipeline needs a repo to checkout the project and cdk files

###
create codestar connection in AWS Toolchain Account ( if you want to use code star. otherwise you have to configure your Github in the source )
### cdk.json
adapt the cdk.json for your accounts, also codestar connection url
adapt account numbers, vpc,  branch names etc
### write and add your stacks
create your own stacks and add to infrastructure folder, add to AppDeploy, write/adapt tests

### commit 
commit your changes to your repo  
before you create the pipeline the cdk.json must be checked in with the current values   
the pipeline will checkout your repo, if the cdk.json is still with xxx values, it will fail  

#### bootstrap the toolchain & stage accounts
bootstrap the toolchain account:  
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
the pipeline template will fail, because the branch is not set. this is ok, it serves just as a template   
for the feature branch pipelines, which will have the branch correctly set, after notifying the pipeline by webhook   

### edit secret ( required for private git access, but secret must be defined anyways for the lambda code )
Edit the secret "github_webhook_secret" in the webconsole to keep a structure like this:
{"SecretString" : "xxxxx"}
important ! 
if you don't adapt the secret, the lambda will fail on this:  secret = get_github_webhook_secret_from_secretsmanager("github_webhook_secret")

### edit github-actions-demo.yml
edit the webhook_url to your api gateway url ( or custom domain) , see .github\workflows   
change action triggers if needed   
otherwise your github cannot notify the api about a new branch  
commit to your repo !

verify your github actions are triggers when you make changes to your repo and call the webhook api without error
![image](https://github.com/wolfgangunger/cdk-codepipeline-multibranch/blob/main/github.jpg)

### create branch and push to see the new feature pipeline gets generated
create a new branch  
git checkout -b feature/branch1  
and push to your repo  
the pipeline will be generated

### create PR and merge 
the pipeline will be destroyed  

## tests
### infrastructure tests
pip install -r requirements.txt
pip install -r requirements-dev.txt

pytest -vvvv -s generic/infrastructure/tests
pytest -vvvv -s infrastructure/tests
### lambda tests 
pytest -vvvv -s infrastructure/lambdas/tests
### integration tests
only dummy tests in this example 
### acceptance tests
only dummy tests in this example 




