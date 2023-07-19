from constructs import Construct
from aws_cdk import (
    Stage,
    DefaultStackSynthesizer,
)

from infrastructure.ecr_stack import EcrStack
from infrastructure.api.github_webhook_api_stack import GithubWebhookAPIStack


class ToolchainDeploy(Stage):
    def __init__(self, scope: Construct, id: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        #githubwebhookapi = GithubWebhookAPIStack(
        #    self,
        #    "github-webhook-api-stack",
        #    config=config,
        #    #pipeline_template="feature-branch-pipeline-template",
        #    pipeline_template="feature-branch-pipeline-generator", 
        #    branch_prefix="^(feature|bug|hotfix)/",
        #    feature_pipeline_suffix="-FeatureBranchPipeline",
        #)
        ## example: ecr repo for toolchain account
        ecr_repo = EcrStack(
            self,
            "EcrRepoStack-toolchain",
            config=config,
            synthesizer=DefaultStackSynthesizer(),
        )
