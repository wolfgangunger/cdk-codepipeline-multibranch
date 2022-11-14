from constructs import Construct
from aws_cdk import (
    Stack,
    aws_iam,
    aws_codepipeline as codepipeline,
    pipelines,
    aws_codebuild,
)

from infrastructure.cicd.toolchain_deploy import ToolchainDeploy


class FeaturePipelineStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        feature_branch_name: str,
        feature_pipeline_suffix: str,
        config: dict = None,
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)

        branch_name = feature_branch_name

        codestar_connection_arn = config.get("connection_arn")
        repo_owner = config.get("owner")
        repo = config.get("repo")

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        accounts = config.get("accounts")
        dev_account: str = accounts["dev"]["account"]
        qa_account: str = accounts["qa"]["account"]
        prod_account: str = accounts["prod"]["account"]

        # synth_dev_account_role_arn = f"arn:aws:iam::{dev_account}:role/caedge-cicd-simulation-codebuild-role-from-toolchain-account"
        # synth_qa_account_role_arn = f"arn:aws:iam::{qa_account}:role/caedge-cicd-simulation-codebuild-role-from-toolchain-account"
        # synth_prod_account_role_arn = f"arn:aws:iam::{prod_account}:role/caedge-cicd-simulation-codebuild-role-from-toolchain-account"

        synth_dev_account_role_arn = (
            f"arn:aws:iam::{dev_account}:role/codebuild-role-from-toolchain-account"
        )

        synth_qa_account_role_arn = (
            f"arn:aws:iam::{qa_account}:role/codebuild-role-from-toolchain-account"
        )
        synth_prod_account_role_arn = (
            f"arn:aws:iam::{prod_account}:role/codebuild-role-from-toolchain-account"
        )

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
            feature_pipeline_suffix,
        )

        pipeline = pipelines.CodePipeline(
            self,
            id,
            pipeline_name=id,
            synth=synth_step,
            code_build_defaults=pipelines.CodeBuildOptions(
                build_environment=aws_codebuild.BuildEnvironment(
                    build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                    privileged=True,
                    environment_variables={
                        "feature_pipeline_suffix": aws_codebuild.BuildEnvironmentVariable(
                            value=feature_pipeline_suffix,
                            type=aws_codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        ),
                    },
                )
            ),
        )

        unit_tests = pipelines.CodeBuildStep(
            "UnitTests",
            input=git_input,
            build_environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            commands=[
                "set -e",
                "pip install -r requirements.txt",
                "pip install -r requirements_dev.txt",
                "pytest -vvvv -s generic/infrastructure/tests",
            ],
            role_policy_statements=[
                aws_iam.PolicyStatement(
                    actions=["S3:ListBucket", "s3:PutObject", "s3:GetObject"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
                aws_iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
            ],
        )

        pipeline.add_wave("UnitTests", post=[unit_tests])

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
                aws_iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
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
            "set -e;BRANCH=$(python infrastructure/scripts/get_branch_name_from_ssm.py); cdk list -c branch_name=$BRANCH",
            "set -e;BRANCH=$(python infrastructure/scripts/get_branch_name_from_ssm.py); cdk synth -c branch_name=$BRANCH",
        ]
        return commands

    def get_unit_tests(
        self,
        git_input,
    ):
        toolchain_unit_tests = pipelines.CodeBuildStep(
            "UnitTests",
            input=git_input,
            build_environment=aws_codebuild.BuildEnvironment(
                build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
            ),
            commands=self.get_unit_tests_commands(),
            role_policy_statements=[
                aws_iam.PolicyStatement(
                    actions=["S3:ListBucket", "s3:PutObject", "s3:GetObject"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
                aws_iam.PolicyStatement(
                    actions=["ssm:GetParameter"],
                    effect=aws_iam.Effect.ALLOW,
                    resources=["*"],
                ),
            ],
        )
        return toolchain_unit_tests

    def get_unit_tests_commands(self) -> list:
        commands = [
            "set -e",
            "pip install -r requirements.txt",
            "pip install -r requirements_dev.txt",
            "pytest -vvvv -s generic/infrastructure/tests",
        ]
        return commands
