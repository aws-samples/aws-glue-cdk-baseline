# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
from typing import Dict
from os import path
from aws_cdk import (
    Stack,
    aws_glue_alpha as glue,
    aws_iam as iam,
)
from constructs import Construct

class GlueAppStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config:Dict, stage:str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.glue_job = glue.Job(self, "ProcessLegislators",
            executable=glue.JobExecutable.python_etl(
                glue_version=glue.GlueVersion.V4_0,
                python_version=glue.PythonVersion.THREE,
                script=glue.Code.from_asset(
                    path.join(path.dirname(__file__), "job_scripts/process_legislators.py")
                )
            ),
            description="an example PySpark job",
            default_arguments={
                "--input_path": config[stage]['jobs']['ProcessLegislators']['inputLocation']
            },
            tags={
                "environment": self.environment,
                "artifact_id": self.artifact_id,
                "stack_id": self.stack_id,
                "stack_name": self.stack_name
            }
        )

        # For integration test
        self.iam_role = iam.Role(self, "GlueTestRole",
            role_name=f"glue-test-{stage}",
            assumed_by=iam.ArnPrincipal(f"arn:aws:iam::{str(config['pipelineAccount']['awsAccountId'])}:root"),
            inline_policies={
                "GluePolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            actions=[
                                "glue:GetJobs",
                                "glue:GetJobRun",
                                "glue:GetTags",
                                "glue:StartJobRun"
                            ],
                            resources=[
                                "*"
                            ]
                        )
                    ]
                )
            }
        )

    @property
    def iam_role_arn(self):
        return self.iam_role.role_arn