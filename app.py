#!/usr/bin/env python3

# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import yaml

import aws_cdk as cdk

from aws_glue_cdk_baseline.pipeline_stack import PipelineStack


app = cdk.App()

# Get target stage from cdk context
config_file = app.node.try_get_context('config')

# Load stage config and set cdk environment
if config_file:
    configFilePath = config_file
else:
    configFilePath = "./default-config.yaml"
with open(configFilePath, 'r', encoding="utf-8") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

PipelineStack(
    app, 
    "PipelineStack",
    config=config,
    env=cdk.Environment(
        account=str(config["pipelineAccount"]["awsAccountId"]), 
        region=config["pipelineAccount"]["awsRegion"]
    )
)

app.synth()
