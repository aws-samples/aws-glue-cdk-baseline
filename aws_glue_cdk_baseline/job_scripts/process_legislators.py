# Copyright 2023 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


class ProcessLegislators:
    def __init__(self):
        params = []
        if '--JOB_NAME' in sys.argv:
            params.append('JOB_NAME')
            params.append('input_path')
        args = getResolvedOptions(sys.argv, params)

        self.context = GlueContext(SparkContext.getOrCreate())
        self.job = Job(self.context)

        if 'JOB_NAME' in args:
            jobname = args['JOB_NAME']
            self.input_path = args['input_path']
        else:
            jobname = "test"
            self.input_path = "s3://awsglue-datasets/examples/us-legislators/all/persons.json"
        self.job.init(jobname, args)
        

    def run(self):
        dyf = read_json(self.context, self.input_path)
        df = dyf.toDF()
        df.printSchema()
        df.show()


def read_json(glue_context, path):
    dynamicframe = glue_context.create_dynamic_frame.from_options(
        connection_type='s3',
        connection_options={
            'paths': [path],
            'recurse': True
        },
        format='json'
    )
    return dynamicframe


if __name__ == '__main__':
    ProcessLegislators().run()
