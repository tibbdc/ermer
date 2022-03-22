import os
from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_ec2 as ec2,
    core
)

class LambdaConstruct(core.Construct):

    def __init__(self,scope:core.Construct,id:str,TargetNeptune="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self.lambda_functions = {}

        # vpc
        vpc = ec2.Vpc.from_lookup(
            self, 
            "default-VPC",
            is_default=True)

        ###################################
        # gremlin layer
        gremlin_layer = _lambda.LayerVersion(
                self, 
                "gremlin-layer",
                code=_lambda.Code.from_asset('lambda/layer-code'),
                compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
                license="Apache-2.0",
                description="A layer to use gremlin api"
            )

        # Lambda: ermer -> gremlin query lambda 
        self.ermer_lambda_function = _lambda.Function(
            self,
            "ermer",
            runtime =_lambda.Runtime.PYTHON_3_8,
            code = _lambda.Code.from_asset('lambda/ermer'),
            handler="app.lambda_handler",
            timeout=core.Duration.seconds(30),
            layers=[gremlin_layer],
            memory_size=1024,
            vpc = vpc,
            vpc_subnets =ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            allow_public_subnet=True,
            security_groups = [TargetNeptune.get_neptune_sg("ermer")],
            environment={
                "neptuneEndpoint":TargetNeptune.get_neptune_cluster("ermer").cluster_read_endpoint.hostname,
                "neptunePort":"8182",
            }
        )

        # neptune grant connection to lambda role
        
        self.lambda_functions["ermer"] = self.ermer_lambda_function

    def get_lambda_functions(self,name):
        return self.lambda_functions[name]
