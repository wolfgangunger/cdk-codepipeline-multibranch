from aws_cdk import (
    DefaultStackSynthesizer,
    Stack,
    Stage,
)

from constructs import Construct
import aws_cdk.aws_iam as aws_iam
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import pipelines
from aws_cdk import aws_codebuild
from aws_cdk.aws_codebuild import BuildEnvironment
from aws_cdk.pipelines import CodePipeline

from infrastructure.cicd.github_webhook_api_stack import GithubWebhookAPIStack
from infrastructure.cicd.feature_pipeline_v2_stack import (
    FeaturePipelineStack,
)

# from infrastructure.cicd import (
#    FastDevPipelineStack,
# )


class PipelineGeneratorApplication(Stage):
    def __init__(
        self,
        scope: Construct,
        id: str,
        pipeline_template: str,
        branch_prefix: str,
        feature_pipeline_suffix: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        GithubWebhookAPIStack(
            self,
            "gitHub-webhook-api",
            pipeline_template=pipeline_template,
            branch_prefix=branch_prefix,
            feature_pipeline_suffix=feature_pipeline_suffix,
            config=config,
            synthesizer=DefaultStackSynthesizer(),
        )

        FeaturePipelineStack(
            self,
            pipeline_template,
            feature_branch_name="not_exist_branch_to_avoid_running",
            feature_pipeline_suffix=feature_pipeline_suffix,
            config={**config},
            synthesizer=DefaultStackSynthesizer(),
        )

        # FastDevPipelineStack(
        #    self,
        #    "fast-dev-pipeline-smart-testing-base",
        #    branch_name="development",
        #    config={**config},
        #    synthesizer=DefaultStackSynthesizer(),
        # )


class PipelineGeneratorStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        branch_name: str,
        pipeline_template: str,
        branch_prefix: str,
        feature_pipeline_suffix: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        accounts = config.get("accounts")
        dev_account: str = accounts["dev"]["account"]
        qa_account: str = accounts["qa"]["account"]
        toolchain_account: str = accounts["tooling"]["account"]
        prod_account: str = accounts["prod"]["account"]
        region: str = accounts["tooling"]["region"]

        synth_dev_account_role_arn = (
            f"arn:aws:iam::{dev_account}:role/codebuild-role-from-toolchain-account"
        )

        synth_qa_account_role_arn = (
            f"arn:aws:iam::{qa_account}:role/codebuild-role-from-toolchain-account"
        )
        synth_prod_account_role_arn = (
            f"arn:aws:iam::{prod_account}:role/codebuild-role-from-toolchain-account"
        )

        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        # creating the pipline with  synch action
        git_input = pipelines.CodePipelineSource.connection(
            repo_string=f"{repo_owner}/{repo}",
            branch=branch_name,
            connection_arn=codestar_connection_arn,
        )
        synth_step = self.get_sync_step(
            git_input,
            synth_dev_account_role_arn,
            synth_qa_account_role_arn,
            synth_prod_account_role_arn,
            branch_name,
        )

        pipeline = CodePipeline(
            self,
            id,
            pipeline_name=id,
            synth=synth_step,
            cross_account_keys=True,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                )
            ),
        )

        tests = pipelines.CodeBuildStep(
            "InfrastructureTests",
            input=git_input,
            build_environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.AMAZON_LINUX_2_3,
                privileged=True,
            ),
            commands=[
                "pip install -r requirements.txt",
                "pip install -r requirements-dev.txt",
                #"pytest -vvvv -s generic/infrastructure/tests",
            ],
        )

        pipeline.add_wave("Testing", post=[tests])

        pipeline_generator_stage = PipelineGeneratorApplication(
            self,
            "pipeline-generator",
            pipeline_template=pipeline_template,
            branch_prefix=branch_prefix,
            feature_pipeline_suffix=feature_pipeline_suffix,
            config=config,
            env={
                "account": toolchain_account,
                "region": region,
            },
        )
        pipeline.add_stage(pipeline_generator_stage)

    ########## methods to be overwritten in subclass
    def get_sync_step(
        self,
        git_input,
        synth_dev_account_role_arn,
        synth_qa_account_role_arn,
        synth_prod_account_role_arn,
        branch_name,
    ):
        synth_step = pipelines.CodeBuildStep(
            "Synth",
            input=git_input,
            commands=self.get_sync_step_commands(),
            env={"BRANCH": branch_name},
            role_policy_statements=[
                aws_iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    effect=aws_iam.Effect.ALLOW,
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
            "echo branch: $BRANCH; cdk list -c branch_name=$BRANCH",
            "echo branch: $BRANCH; cdk synth -c branch_name=$BRANCH",
        ]
        return commands
