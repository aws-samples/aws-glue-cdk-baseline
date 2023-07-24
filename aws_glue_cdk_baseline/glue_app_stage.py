# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from typing import Dict
import aws_cdk as cdk
from constructs import Construct
from aws_glue_cdk_baseline.glue_app_stack import GlueAppStack

class GlueAppStage(cdk.Stage):
    def __init__(self, scope: Construct, construct_id: str, config:Dict, stage:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.glue_app_stack = GlueAppStack(self, "GlueAppStack", config, stage)

    @property
    def iam_role_arn(self):
        return self.glue_app_stack.iam_role_arn
