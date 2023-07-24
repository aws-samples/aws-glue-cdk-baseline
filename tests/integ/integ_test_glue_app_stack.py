# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import sys
import pytest
import argparse
import concurrent.futures
import logging
import boto3
from botocore.waiter import WaiterModel
from botocore.waiter import create_waiter_with_client

parser = argparse.ArgumentParser()
parser.add_argument('--account', dest='account', type=str, help='The AWS account ID.')
parser.add_argument('--region', dest='region', type=str, help='The AWS Region name.')
parser.add_argument('--stage-name', dest='stage_name', type=str, help='Stage name.')
parser.add_argument('--sts-role-arn', dest='sts_role_arn', type=str, help='The AWS STS role ARN.')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", help='(Optional) Display verbose logging (default: false)')
args, unknown = parser.parse_known_args()

logger = logging.getLogger()
logger_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(logger_handler)
if args.verbose:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
for libname in ["boto3", "botocore", "urllib3", "s3transfer"]:
    logging.getLogger(libname).setLevel(logging.WARNING)

waiter_name = "JobRunCompleted"
waiter_config = {
    "version": 2,
    "waiters": {
        "JobRunCompleted": {
            "operation": "GetJobRun",
            "delay": 60,
            "maxAttempts": 30,
            "acceptors": [
                {
                    "matcher": "path",
                    "expected": "SUCCEEDED",
                    "argument": "JobRun.JobRunState",
                    "state": "success"
                },
                {
                    "matcher": "path",
                    "expected": "FAILED",
                    "argument": "JobRun.JobRunState",
                    "state": "failure"
                },
                {
                    "matcher": "path",
                    "expected": "STOPPED",
                    "argument": "JobRun.JobRunState",
                    "state": "failure"
                },
                {
                    "matcher": "path",
                    "expected": "TIMEOUT",
                    "argument": "JobRun.JobRunState",
                    "state": "failure"
                },
                {
                    "matcher": "path",
                    "expected": "ERROR",
                    "argument": "JobRun.JobRunState",
                    "state": "failure"
                }
            ]
        }
    }
}
waiter_model = WaiterModel(waiter_config)


def integ_test_glue_job(glue_client, glue_job_run_waiter, account, region, job_name, stage_name):
    logger.debug(f"Checking tags of job: {job_name}")
    res = glue_client.get_tags(
        ResourceArn=f"arn:aws:glue:{region}:{account}:job/{job_name}"
    )
    tags = res["Tags"]
    if not tags.get("stack_name") or not tags["stack_name"].startswith(stage_name):
        logger.debug(f"Skipping job: {job_name}")
        return

    logger.info(f"Performing integ test of job: {job_name}")

    res = glue_client.start_job_run(
        JobName=job_name
    )
    jobrun_id = res["JobRunId"]

    glue_job_run_waiter.wait(JobName=job_name, RunId=jobrun_id)
    res = glue_client.get_job_run(
        JobName=job_name,
        RunId=jobrun_id
    )

    state = res["JobRun"]["JobRunState"]
    duration = int(res["JobRun"]["ExecutionTime"])
    logger.info(f"Completed integ test of job: {job_name}")
    logger.info(f" - Job state: {state}")
    logger.info(f" - Job duration: {duration}")

    assert state == "SUCCEEDED"
    assert duration < 600

def integ_test_glue_app_stack(glue_client, glue_job_run_waiter, account, region, stage_name):
    jobs = []
    get_jobs_paginator = glue_client.get_paginator("get_jobs")
    for page in get_jobs_paginator.paginate():
        jobs.extend(page["Jobs"])

    job_names = []
    for j in jobs:
        job_name = j["Name"]
        job_names.append(job_name)

    # Multi-threading per-job tests
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_partition = {executor.submit(
            integ_test_glue_job, glue_client, glue_job_run_waiter, account, region, job_name, stage_name): job_name for job_name in job_names}
        for future in concurrent.futures.as_completed(future_to_partition):
            partition = future_to_partition[future]
            data = future.result()


def main():
    initial_session = boto3.Session(region_name=args.region)
    sts = initial_session.client("sts")
    res = sts.assume_role(RoleArn=args.sts_role_arn, RoleSessionName='glue-integ-test')

    session_args = {}
    session_args['region_name'] = args.region
    session_args['aws_access_key_id'] = res['Credentials']['AccessKeyId']
    session_args['aws_secret_access_key'] = res['Credentials']['SecretAccessKey']
    session_args['aws_session_token'] = res['Credentials']['SessionToken']

    session = boto3.Session(**session_args)
    glue = session.client("glue")
    job_run_waiter = create_waiter_with_client(waiter_name, waiter_model, glue)

    integ_test_glue_app_stack(
        glue_client=glue,
        glue_job_run_waiter=job_run_waiter,
        account=args.account, 
        region=args.region, 
        stage_name=args.stage_name
    )

if __name__ == "__main__":
    main()
