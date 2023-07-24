# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_glue_cdk_baseline.glue_app_stack import GlueAppStack

config = {
    "pipelineAccount": {
        "awsAccountId": 123456789101,
        "awsRegion": "us-east-1"
    },
    "dev": {
        "jobs": {
            "ProcessLegislators": {
                "inputLocation": "s3://path_to_data/"
            }
        }
    }
}

def test_glue_job_created():
    app = core.App()
    stack = GlueAppStack(
        app, "TestGlueAppStack",
        config=config,
        stage="dev",
        env=core.Environment(region=str(config["pipelineAccount"]["awsAccountId"]))
    )
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Glue::Job", {
        "Command": {
            "Name": "glueetl"
        },
        "GlueVersion": "4.0"
    })
