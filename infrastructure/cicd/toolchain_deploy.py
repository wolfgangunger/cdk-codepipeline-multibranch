from constructs import Construct
from aws_cdk import (
    Stage,
    DefaultStackSynthesizer,
)

from infrastructure.data.ecr_stack import EcrStack


class ToolchainDeploy(Stage):
    def __init__(self, scope: Construct, id: str, config: dict = None, **kwargs):
        super().__init__(scope, id, **kwargs)

        ## example stack which should be deployed on toolchain account
        ecr_repo = EcrStack(
            self,
            "EcrRepoStack-toolchain",
            config=config,
            synthesizer=DefaultStackSynthesizer(),
        )
