from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr,
)


class EcrStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        config: dict = None,
        **kwargs,
    ) -> None:
        super().__init__(scope=scope, id=id, stack_name=id, **kwargs)

        repo = aws_ecr.Repository(self, "ecr-repo-1")
