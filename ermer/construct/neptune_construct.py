import os

from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_neptune as neptune
    )
from aws_cdk.aws_ecr_assets import DockerImageAsset

class NeptuneConstruct(core.Construct):

    def __init__(self,scope:core.Construct,id:str,TargetS3="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self.clusters ={}
        self.security_groups ={}
        ###########################################
        # vpc
        ###########################################
        vpc = ec2.Vpc.from_lookup(
            self, 
            "default-VPC",
            is_default=True)

        # sg
        my_security_group = ec2.SecurityGroup(self, "ermer-neptune-sg",
            vpc=vpc,
            description="Allow default sg 8182 access to Neptune",
            allow_all_outbound=True
        )
        my_security_group.add_ingress_rule(my_security_group, ec2.Port.tcp(8182), "allow all 8182 access in defaut")

        # Neptune IAM role
        # api role
        self.neptune_role = iam.Role(
            self,
            "neptune-role",
            assumed_by = iam.ServicePrincipal(
                "rds.amazonaws.com"
            )
        )
        TargetS3.get_s3_bucket('ermer').grant_read(self.neptune_role)

        # T3 Medium Neptune cluster
        cluster = neptune.DatabaseCluster(
            self, 
            "ermer",
            vpc=vpc,
            associated_roles = [self.neptune_role],
            instance_type=neptune.InstanceType.T3_MEDIUM,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_groups=[my_security_group],
        )

        self.clusters["ermer"] = cluster
        self.security_groups["ermer"] = my_security_group

        # output neptune role arn 
        core.CfnOutput(
            self,
            "NeptuneRoleArn",
            value=self.neptune_role.role_arn
        )

        # output neptune role arn 
        core.CfnOutput(
            self,
            "NeptuneClusterEndpoints",
            value=cluster.cluster_read_endpoint.hostname
        )
    def get_neptune_cluster(self,name):
        return self.clusters[name]
    def get_neptune_sg(self,name):
        return self.security_groups[name]
