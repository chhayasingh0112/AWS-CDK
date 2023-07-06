from aws_cdk import (
    core,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_assets as s3_assets,
)
from app import MyStack

class PipelineStack(core.Stack):
    def _init_(self, scope: core.Construct, id: str, cdk_stack: MyStack, **kwargs) -> None:
        super()._init_(scope, id, **kwargs)

        # Define the CodeCommit repository
        repository = codecommit.Repository.from_repository_name(
            self,  "MyRepository", repository_name=cdk_stack.repository.repository_name
        )

        # Define the source action for CodePipeline
        source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit_Source",
            repository=repository,
            branch="main",
            output=source_output
        )

        # Define the build action for CodePipeline
        build_project = codebuild.PipelineProject(
            self,
            "MyBuildProject",
            build_spec=codebuild.BuildSpec.from_object({
                "version": "0.2",
                "phases": {
                    "install": {
                        "commands": [
                            "pip3 install aws-cdk.core",
                            "pip3 install aws-cdk.aws_iam",
                            "pip3 install aws-cdk.aws_s3",
                        ]
                    },
                    "build": {
                        "commands": [
                            # Add commands to build your Python/JS app here
                            # For example, running tests, bundling, etc.
                            "python3 -m unittest discover -s tests -p '*test_*.py'",
                            "python3 setup.py bdist_wheel"
                        ]
                    }
                },
                "artifacts": {
                    "files": [
                        "**/*"
                    ],
                    "discard-paths": "yes"
                }
            }),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
            )
        )
        build_output = codepipeline.Artifact()
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild_Build",
            project=build_project,
            input=source_output,
            outputs=[build_output]
        )

        # Define deployment to S3
        deploy_action = codepipeline_actions.S3DeployAction(
            action_name="DeployToS3",
            input=build_output,
            bucket=cdk_stack.artifacts_bucket,
            object_key='artifact.zip',
            extract=True
        )

        # Create the CodePipeline
        pipeline = codepipeline.Pipeline(
            self,
            "MyPipeline",
            pipeline_name="MyPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                ),
                codepipeline.StageProps(
                    stage_name="Deploy",
                    actions=[deploy_action]
                )
            ]
        )

app = core.App()
env = core.Environment(account="717005702476", region="us-east-1")

my_stack = MyStack(app, "test-cdk", env=env)
PipelineStack(app, "my-pipeline-stack", cdk_stack=my_stack, env=env)

app.synth()