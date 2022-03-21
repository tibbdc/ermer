from aws_cdk import core as cdk
from ermer.construct.s3_construct import S3Construct
from ermer.construct.lambda_construct import LambdaConstruct
from ermer.construct.apigateway_construct import APIConstruct
from ermer.construct.neptune_construct import NeptuneConstruct

from aws_cdk import core


class ErmerStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, Stage="default", **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Definition of S3
        self.My_S3_Bucket = S3Construct(
            self,
            "s3-construct",
            Stage=Stage
        )

        # Definition of Neptune
        self.My_Neptune = NeptuneConstruct(
            self,
            "neptune-construct",
            TargetS3 = self.My_S3_Bucket,
            Stage=Stage
        )
        
        # Definition of Lambda func
        self.My_Lambda_Func = LambdaConstruct(
            self,
            "lambda-construct",
            TargetNeptune = self.My_Neptune,
            Stage=Stage
        )
        
        # Definiton of API Gateway
        self.My_API_Gateway = APIConstruct(
            self,
            "apigateway-construct",
            TargetLambda = self.My_Lambda_Func,
            Stage=Stage
        )

