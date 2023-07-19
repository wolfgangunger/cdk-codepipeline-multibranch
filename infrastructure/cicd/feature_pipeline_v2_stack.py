from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    pipelines,
    aws_codebuild,
    Duration,
)
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodePipeline

from infrastructure.cicd.app_deploy import AppDeploy, AppDeployBootstrap
from infrastructure.cicd.toolchain_deploy import ToolchainDeploy
from infrastructure.cicd.toolchain_deploy import ToolchainDeploy

from generic.infrastructure.cicd.pipeline_stack import PipelineStack

class FeaturePipelineStack(PipelineStack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        feature_branch_name: str,
        feature_pipeline_suffix: str,
        config: dict = None,
        **kwargs,
    ):
        
        super().__init__(
            scope,
            id,
            development_pipeline=True,
            config=config,
            **kwargs,
        )
    
# this is the feature branch pipeline 
# it got the same superclass as the normal pipeline, thus same actions to synth, deploy and test
# you can setup a different feature pipline clss instead, for example without deployment or with less testes or whatever
# you can also create different pipelines with the pipeline generator, for example faster pipelines with less methods/actions
# or full piplines

    ## overwritten methods
    ## the source step must be overwritten for branch name
    def get_connection(
        self,
        repo_owner,
        repo,
        config,
        development_pipeline,
        codestar_connection_arn
    ):
        git_input = pipelines.CodePipelineSource.connection(
            repo_string=f"{repo_owner}/{repo}",
            branch=self.feature_branch_name,
            connection_arn=codestar_connection_arn,
        )
        return git_input
    ## the synth step must be overwritten to adapt the branch name
    def get_sync_step(
        self,
        git_input,
        synth_dev_account_role_arn,
        synth_qa_account_role_arn,
        synth_prod_account_role_arn,
        feature_pipeline_suffix,
    ):
        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=git_input,
            build_environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            commands=self.get_sync_step_commands(),
            env={"feature_pipeline_suffix": feature_pipeline_suffix},
            role_policy_statements=[
                iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    effect=iam.Effect.ALLOW,
                    resources=["*"],
                ),
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        synth_dev_account_role_arn,
                        synth_qa_account_role_arn,
                        synth_prod_account_role_arn,
                    ],
                ),
            ],
        )
        return synth_step

    def get_sync_step_commands(self) -> list:
        commands = [
            "npm install -g aws-cdk",
            "python -m pip install -r requirements.txt",
            "set -e;BRANCH=$(python infrastructure/scripts/get_branch_name_from_ssm.py); cdk list -c branch_name=$BRANCH",
            "set -e;BRANCH=$(python infrastructure/scripts/get_branch_name_from_ssm.py); cdk synth -c branch_name=$BRANCH",
        ]
        return commands




