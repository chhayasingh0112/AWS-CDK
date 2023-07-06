from aws_cdk import core
from aws_cdk import (
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_codecommit as codecommit
)

class MyStack(core.Stack):

    def _init_(self, scope: core.Construct, id: str, **kwargs) -> None:
        super()._init_(scope, id, **kwargs)

        # Create CodeCommit Repository
        self.repository = codecommit.Repository(self, "TestRepository",
            repository_name="TestRepository",
            description="Test repository created with CDK",
        )

        # Create S3 Bucket
        self.artifacts_bucket = s3.Bucket(self, "TestBucket",
            bucket_name="my-test-bucket-cdk-02072023",  # Replace with the desired bucket name
            versioned=True,
            removal_policy=core.RemovalPolicy.DESTROY
        )

        # Create an EC2 instance
        self.vpc = ec2.Vpc(self, "VPC",
            cidr="10.1.0.0/16",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="Public", cidr_mask=24, subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name="Private", cidr_mask=24, subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
            ]
        )

        self.security_group = ec2.SecurityGroup(self, "SecurityGroup",
            vpc=self.vpc,
            description="Allow ssh access to ec2 instances",
            allow_all_outbound=True
        )
        self.security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22))

        self.instance = ec2.Instance(self, "Instance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=self.vpc,
            security_group=self.security_group,
        )


app = core.App()
MyStack(app, "test-cdk")
app.synth()