# AWS Glue CDK baseline template

This is a baseline template for AWS CDK development with AWS Glue.
This CDK template is built with [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/home.html) and [AWS CDK Pipelines](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html).

Typically, you have multiple accounts to manage and provision resources for your data pipeline. In this template, we assume the following three accounts:
* Pipeline account - This hosts the end-to-end pipeline
* Dev account – This hosts the integration pipeline in the development environment
* Prod account – This hosts the data integration pipeline in the production environment

If you want, you can use the same account and the same Region for all three.

To start applying this end-to-end development lifecycle model to your data platform easily and quickly, we prepared [a baseline template `aws-glue-cdk-baseline` using AWS CDK](https://github.com/aws-samples/aws-glue-cdk-baseline). The template is built on top of [AWS CDK v2](https://docs.aws.amazon.com/cdk/v2/guide/home.html) and [AWS CDK Pipelines](https://docs.aws.amazon.com/cdk/v2/guide/cdk_pipeline.html). It provisions two kinds of stacks; 

* AWS Glue app stack – This provisions the data integration pipeline: one in the dev account and one in the prod account
* Pipeline stack – This provisions the Git repository and CI/CD pipeline in the pipeline account

The AWS Glue app stack provisions the data integration pipeline, including the following resources:

* AWS Glue jobs
* AWS Glue job scripts

At the time of publishing of this template, the AWS CDK has two versions of the AWS Glue module: [@aws-cdk/aws-glue](https://docs.aws.amazon.com/cdk/api/v1/docs/aws-glue-readme.html) and [@aws-cdk/aws-glue-alpha](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-glue-alpha-readme.html), containing [L1 constructs](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html#constructs_l1_using) and [L2 constructs](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html#constructs_using), respectively. The sample Glue app stack is defined using [aws-glue-alpha](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-glue-alpha-readme.html), [the L2 construct](https://docs.aws.amazon.com/cdk/v2/guide/constructs.html#constructs_using) for AWS Glue because it’s straightforward to define and manage AWS Glue resources. If you want to use the L1 construct, refer to [Build, Test and Deploy ETL solutions using AWS Glue and AWS CDK based CI/CD pipelines](https://aws.amazon.com/blogs/big-data/build-test-and-deploy-etl-solutions-using-aws-glue-and-aws-cdk-based-ci-cd-pipelines/).

The pipeline stack provisions the entire CI/CD pipeline, including the following resources:

* AWS IAM roles
* Amazon S3 bucket
* AWS CodeCommit
* AWS CodePipeline
* AWS CodeBuild

Every time the business requirement changes (such as adding data sources or changing data transformation logic), you make changes on the AWS Glue app stack and re-provision the stack to reflect your changes. This is done by committing your changes in the AWS CDK template to the CodeCommit repository, then CodePipeline reflects changes on AWS resources using [AWS CloudFormation change sets](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-changesets.html).

In the following sections, we present the steps to set up the required environment and demonstrate the end-to-end development lifecycle.

### Pre-requisite

* Python 3.9 or later
* AWS accounts for Pipeline account, Dev account, and Prod account
* [AWS Named profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for Pipeline account, Dev account, and Prod account
* The [AWS CDK Toolkit (cdk command)](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) 2.87.0 or later
* Docker
* [Visual Studio Code](https://code.visualstudio.com/)
* [Visual Studio Code Dev Containers](https://code.visualstudio.com/docs/remote/containers)

### Initialize the project

To initialize the project, complete the following steps:

1. Clone [the baseline template](https://github.com/aws-samples/aws-glue-cdk-baseline) to your workplace.

```
$ git clone git@github.com:aws-samples/aws-glue-cdk-baseline.git
$ cd aws-glue-cdk-baseline.git
```

2. Create a Python [virtual environment](https://docs.python.org/3/library/venv.html) specific to the project on the client machine. 

```
$ python3 -m venv .venv
```

We use a virtual environment in order to isolate the Python environment for this project and not install software globally.

3. Activate the virtual environment according to your OS:

* On MacOS and Linux, use the following code:

```
$ source .venv/bin/activate
```

* On a Windows platform, use the following code:

```
% .venv\Scripts\activate.bat
```

After this step, the subsequent steps run within the bounds of the virtual environment on the client machine and interact with the AWS account as needed.

4. Install the required dependencies described in [requirements.txt](https://github.com/aws-samples/aws-glue-cdk-cicd/blob/main/requirements.txt) to the virtual environment:

```
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```


5. Edit the configuration file `default-config.yaml` based on your environments (replace each account ID with your own): 

```
pipelineAccount:
  awsAccountId: 123456789101
  awsRegion: us-east-1

devAccount:
  awsAccountId: 123456789102
  awsRegion: us-east-1

prodAccount:
  awsAccountId: 123456789103
  awsRegion: us-east-1
```

6. Run `pytest` to initialize the snapshot test files by running following command:

```
$ python3 -m pytest --snapshot-update
```

### Bootstrap your AWS environments

Run the following commands to bootstrap your AWS environments.

1. In the pipeline account, replace `PIPELINE-ACCOUNT-NUMBER`, `REGION`, and `PIPELINE-PROFILE` with your own values: 

```
$ cdk bootstrap aws://<PIPELINE-ACCOUNT-NUMBER>/<REGION> --profile <PIPELINE-PROFILE> \
    --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess
```

2. In the dev account, replace `DEV-ACCOUNT-NUMBER`, `REGION`, and `DEV-PROFILE` with your own values: 

```
$ cdk bootstrap aws://<DEV-ACCOUNT-NUMBER>/<REGION> --profile <DEV-PROFILE> \
    --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
    --trust PIPELINE-ACCOUNT-NUMBER
```

3. In the prod account, replace `PROD-ACCOUNT-NUMBER`, `REGION`, and `PROD-PROFILE` with your own values: 

```
$ cdk bootstrap aws://<PROD-ACCOUNT-NUMBER>/<REGION> --profile <PROD-PROFILE> \
    --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess \
    --trust PIPELINE-ACCOUNT-NUMBER
```

When you use only one account for all environments, you can just run the `cdk bootstrap` command one time.

### Deploy your AWS resources

Run the command using Pipeline account to deploy resources defined in the AWS CDK baseline template:

```
$ cdk deploy --profile <PIPELINE-PROFILE>
```

This creates the pipeline stack in the pipeline account and the AWS Glue app stack in the development account.

When the `cdk deploy` command is completed, let’s verify the pipeline using the pipeline account.

1. Open [AWS CodePipeline console](https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines).
2. Choose `GluePipeline`.

Then verify that GluePipeline has stages; `Source`, `Build`, `UpdatePipeline`, `Assets`, `DeployDev`, and `DeployProd`. Also verify that these five stages `Source`, `Build`, `UpdatePipeline`, `Assets`, `DeployDev` have been succeeded, and `DeployProd` is in pending status. It can take about 15 minutes.

Now that the pipeline has been created successfully, you can also verify the AWS Glue app stack resource on the AWS CloudFormation console in the dev account.
At this step, the AWS Glue app stack is deployed only in the dev account. You can try to run the AWS Glue job `ProcessLegislators` to see how it works.

### Configure your Git repository with AWS CodeCommit

In the earlier step, you cloned the Git repository from GitHub. Although it is possible to configure the CDK template to work with GitHub, GitHub Enterprise, or Bitbucket, this time we use AWS CodeCommit. If you prefer those 3rd party Git providers, [configure connections](https://docs.aws.amazon.com/codepipeline/latest/userguide/connections-github.html), and edit `[pipeline_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/aws_glue_cdk_baseline/pipeline_stack.py)` to define the variable `source` to use the target Git provider using `[CodePipelineSource](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.pipelines.CodePipelineSource.html)`.

Because you already ran the `cdk deploy` command, the CodeCommit repository has already been created with all the required code and related files. The first step is to [setup required for access to CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-migrate-repository-existing.html#how-to-migrate-existing-setup). The next step is to clone the repository from the CodeCommit repository to your local. Run the following commands:

```
$ mkdir aws-glue-cdk-baseline-codecommit
$ cd aws-glue-cdk-baseline-codecommit
$ git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/aws-glue-cdk-baseline
```

In the next step, we make changes in this local copy of the CodeCommit repository.

## End-to-end development lifecycle

Now that the environment has been successfully created, you’re ready to start developing a data integration pipeline using this baseline template. Let’s walk through end-to-end development lifecycle.

When you want to define your own data integration pipeline, you need to add more AWS Glue jobs and implement job scripts. For this tutorial, let’s assume the use case to add a new AWS Glue job with a new job script to read multiple S3 locations and join them.

### Implement and test in your local

First, implement and test the AWS Glue job and its job script in your local environment using Visual Studio Code.

Set up your development environment by following the steps in [Develop and test AWS Glue version 3.0 and 4.0 jobs locally using a Docker container](https://aws.amazon.com/blogs/big-data/develop-and-test-aws-glue-version-3-0-jobs-locally-using-a-docker-container/). The following steps are required in the context of this template.

1. Start Docker.
2. Pull the Docker image which has local development environment using AWS Glue ETL library:

```
$ docker pull `public.ecr.aws/glue/aws-glue-libs:glue_libs_4.0.0_image_01`
```

3. Run the following command to define AWS named profile name:

```
$ PROFILE_NAME="<DEV-PROFILE>"
```

4. Run the following command to make it available with the baseline template:

```
$ cd aws-glue-cdk-baseline/
$ WORKSPACE_LOCATION=$(pwd)
```

5. Run the Docker container:

```
$ docker run -it -v ~/.aws:/home/glue_user/.aws -v $WORKSPACE_LOCATION:/home/glue_user/workspace/ -e AWS_PROFILE=$PROFILE_NAME -e DISABLE_SSL=true --rm -p 4040:4040 -p 18080:18080 --name glue_pyspark public.ecr.aws/glue/aws-glue-libs:glue_libs_4.0.0_image_01 pyspark
```

6. Start Visual Studio Code. 
7. Choose **Remote Explorer** in the navigation pane, and choose the arrow icon of the `workspace` folder in the container `public.ecr.aws/glue/aws-glue-libs:glue_libs_4.0.0_image_01`.

If the workspace folder is not shown up, choose **Open folder** and select `/home/glue_user/workspace`.

Now you install the required dependencies described in [requirements.txt](https://github.com/aws-samples/aws-glue-cdk-cicd/blob/main/requirements.txt) to the container environment. 

8. Run the following commands in [the terminal in Visual Studio Code](https://code.visualstudio.com/docs/terminal/basics):

```
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

9. Implement the code.

Now let’s make the required changes for a new AWS Glue job here.

* `[aws_glue_cdk_baseline/glue_app_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/aws_glue_cdk_baseline/glue_app_stack.py)`

Let’s add this new code block right after the existing job definition of `ProcessLegislators` in order to add the new Glue job `JoinLegislators`:

```python
        self.new_glue_job = glue.Job(self, "JoinLegislators",
            executable=glue.JobExecutable.python_etl(
                glue_version=glue.GlueVersion.V4_0,
                python_version=glue.PythonVersion.THREE,
                script=glue.Code.from_asset(
                    path.join(path.dirname(__file__), "job_scripts/join_legislators.py")
                )
            ),
            description="a new example PySpark job",
            default_arguments={
                "--input_path_orgs": config[stage]['jobs']['JoinLegislators']['inputLocationOrgs'],
                "--input_path_persons": config[stage]['jobs']['JoinLegislators']['inputLocationPersons'],
                "--input_path_memberships": config[stage]['jobs']['JoinLegislators']['inputLocationMemberships']
            },
            tags={
                "environment": self.environment,
                "artifact_id": self.artifact_id,
                "stack_id": self.stack_id,
                "stack_name": self.stack_name
            }
        )
```

Here, you added three job parameters for different S3 locations. In the proceeding steps, you will provide those locations through the Glue job parameters.

Then, create a new job script, and a new unit test script for the new Glue job:

* `aws_glue_cdk_baseline/job_scripts/join_legislators.py`

```python
import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import Join
from awsglue.utils import getResolvedOptions


class JoinLegislators:
    def __init__(self):
        params = []
        if '--JOB_NAME' in sys.argv:
            params.append('JOB_NAME')
            params.append('input_path_orgs')
            params.append('input_path_persons')
            params.append('input_path_memberships')
        args = getResolvedOptions(sys.argv, params)

        self.context = GlueContext(SparkContext.getOrCreate())
        self.job = Job(self.context)

        if 'JOB_NAME' in args:
            jobname = args['JOB_NAME']
            self.input_path_orgs = args['input_path_orgs']
            self.input_path_persons = args['input_path_persons']
            self.input_path_memberships = args['input_path_memberships']
        else:
            jobname = "test"
            self.input_path_orgs = "s3://awsglue-datasets/examples/us-legislators/all/organizations.json"
            self.input_path_persons = "s3://awsglue-datasets/examples/us-legislators/all/persons.json"
            self.input_path_memberships = "s3://awsglue-datasets/examples/us-legislators/all/memberships.json"
        self.job.init(jobname, args)
    
    def run(self):
        dyf = join_legislators(self.context, self.input_path_orgs, self.input_path_persons, self.input_path_memberships)
        df = dyf.toDF()
        df.printSchema()
        df.show()
        print(df.count())

def read_dynamic_frame_from_json(glue_context, path):
    return glue_context.create_dynamic_frame.from_options(
        connection_type='s3',
        connection_options={
            'paths': [path],
            'recurse': True
        },
        format='json'
    )

def join_legislators(glue_context, path_orgs, path_persons, path_memberships):
    orgs = read_dynamic_frame_from_json(glue_context, path_orgs)
    persons = read_dynamic_frame_from_json(glue_context, path_persons)
    memberships = read_dynamic_frame_from_json(glue_context, path_memberships)
    orgs = orgs.drop_fields(['other_names', 'identifiers']).rename_field('id', 'org_id').rename_field('name', 'org_name')
    dynamicframe_joined = Join.apply(orgs, Join.apply(persons, memberships, 'id', 'person_id'), 'org_id', 'organization_id').drop_fields(['person_id', 'org_id'])
    return dynamicframe_joined

if __name__ == '__main__':
    JoinLegislators().run()
```

* `aws_glue_cdk_baseline/job_scripts/tests/test_join_legislators.py`

```python
import pytest
import sys
import join_legislators
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions


@pytest.fixture(scope="module", autouse=True)
def glue_context():
    sys.argv.append('--JOB_NAME')
    sys.argv.append('test_count')

    args = getResolvedOptions(sys.argv, ['JOB_NAME'])
    context = GlueContext(SparkContext.getOrCreate())
    job = Job(context)
    job.init(args['JOB_NAME'], args)

    yield(context)


def test_counts(glue_context):
    dyf = join_legislators.join_legislators(glue_context, 
        "s3://awsglue-datasets/examples/us-legislators/all/organizations.json",
        "s3://awsglue-datasets/examples/us-legislators/all/persons.json", 
        "s3://awsglue-datasets/examples/us-legislators/all/memberships.json")
    assert dyf.toDF().count() == 10439
```

* `[default-config.yaml](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/default-config.yaml)`

Add following under `prod` and `dev`:

```yaml
    JoinLegislators:
      inputLocationOrgs: "s3://awsglue-datasets/examples/us-legislators/all/organizations.json"
      inputLocationPersons: "s3://awsglue-datasets/examples/us-legislators/all/persons.json"
      inputLocationMemberships: "s3://awsglue-datasets/examples/us-legislators/all/memberships.json"
```

* `[tests/unit/test_glue_app_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/tests/unit/test_glue_app_stack.py)`
* `[tests/unit/test_pipeline_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/tests/unit/test_pipeline_stack.py)`
* `[tests/snapshot/test_snapshot_glue_app_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/tests/snapshot/test_snapshot_glue_app_stack.py)`

Add following under `"jobs"` in the variable `config` in the above three files (No need to replace S3 locations): 

```python
            ,
            "JoinLegislators": {
                "inputLocationOrgs": "s3://path_to_data_orgs",
                "inputLocationPersons": "s3://path_to_data_persons",
                "inputLocationMemberships": "s3://path_to_data_memberships"
            }
```

10. Choose **Run** at the top right to run individual job scripts. If **Run** button is not shown, install **Python** into the container through **Extensions** in the navigation pane.
11. For local unit testing, run following command in [the terminal in Visual Studio Code](https://code.visualstudio.com/docs/terminal/basics):

```
$ cd aws_glue_cdk_baseline/job_scripts/
$ python3 -m pytest
```

Then you can verify that the newly added unit test passed successfully.

12. Run `pytest` to initialize the snapshot test files by running following command:

```
$ cd ../../
$ python3 -m pytest --snapshot-update
```

### Deploy to development environment

Complete following steps to deploy the AWS Glue app stack to the development environment and run integration tests there:

1. [Setup required for access to CodeCommit](https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-migrate-repository-existing.html#how-to-migrate-existing-setup). 
2. Commit and push your changes to AWS CodeCommit repo.

```
$ git add .
$ git commit -m "Add the second Glue job"
$ git push
```

You can see that the pipeline is successfully triggered.

### Integration test

There is nothing required for running the integration test for newly added Glue job. The integration test script `[integ_test_glue_app_stack.py](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/tests/integ/integ_test_glue_app_stack.py)` runs all the jobs including a specific tag, then verify the state and its duration. If you want to change the condition or the threshold, you can edit assertions at [the end of `integ_test_glue_job` method](https://github.com/aws-samples/aws-glue-cdk-baseline/blob/main/tests/integ/integ_test_glue_app_stack.py#L105-L106).

### Deploy to production environment

Complete the following steps to deploy the AWS Glue app stack to the production environment:

1. On the `GluePipeline` page in the [AWS CodePipeline console](https://us-east-1.console.aws.amazon.com/codesuite/codepipeline/pipelines), choose **Review** under `DeployProd` stage.
2. Choose **Approve**.

Wait for the `DeployProd` stage to be completed, then you can verify the AWS Glue app stack resource in the dev account.


## Clean up

For cleaning up your resources, complete following steps:

1. Run the following command using Pipeline account:

```
$ cdk destroy --profile <PIPELINE-PROFILE>
```

2. Delete the AWS Glue app stack in the dev account and prod account.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
