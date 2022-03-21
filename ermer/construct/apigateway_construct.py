import os
import json
import configparser
from aws_cdk import (
    aws_iam as iam,
    aws_apigateway as apigw,
    core,
)

class APIConstruct(core.Construct):    

    def __init__(self,scope:core.Construct,id:str,TargetLambda="default",Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)

        self._method_arns = []
        
        # api role
        self.api_role = iam.Role(
            self,
            "api_role",
            assumed_by = iam.ServicePrincipal(
                "apigateway.amazonaws.com"
            )
        )

        # api gateway endpoint
        self._api = apigw.RestApi(
            self, 
            'ermer'
        )


        ########################################
        # resources
        # simple search,  Interactive Search 1st query
        entity_simple = self._api.root.add_resource('simple')
        # post
        entity_simple_intergration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('ermer'),
            proxy=True,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )
        
        simple_post_method = entity_simple.add_method(
            'POST',
            entity_simple_intergration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                }
            }
        ]
        )
        self._method_arns.append(
            simple_post_method.method_arn
        )
        # cors
        self.add_cors_options(entity_simple)

        ########################################
        # resource 
        # deep search, Interactive Search 2nd query
        entity_deep = self._api.root.add_resource("deep")
        entity_deep_integration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('ermer'),
            proxy=True,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )

        entity_deep_method = entity_deep.add_method(
            "POST",
            entity_deep_integration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                }
            ]
        )
        self._method_arns.append(
            entity_deep_method.method_arn
        )
        # cors
        self.add_cors_options(entity_deep)

        ########################################
        # resource 
        # regulation search,  Regulation Search
        entity_regulation = self._api.root.add_resource('regulation')
        entity_regulation_integration = apigw.LambdaIntegration(
            TargetLambda.get_lambda_functions('ermer'),
            proxy=True,
            integration_responses=[
            {
                'statusCode': '200',
                'responseParameters': {
                'method.response.header.Access-Control-Allow-Origin': "'*'",
                }
            }
                ],
        )

        entity_regulation_method = entity_regulation.add_method(
            "POST",
            entity_regulation_integration,
            authorization_type=apigw.AuthorizationType.IAM,
            method_responses=[{
                    'statusCode': '200',
                    'responseParameters': {
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                }
            ]
        )
        self._method_arns.append(
            entity_regulation_method.method_arn
        )

        # cors
        self.add_cors_options(entity_regulation)


    def get_method_arns(self):
        return self._method_arns

        
    def get_method_arns(self):
        return self._method_arns


    ## add CORS to api
    def add_cors_options(self, apigw_resource):
        apigw_resource.add_method(
            'OPTIONS',
            apigw.MockIntegration(
                integration_responses=[
                    {
                        'statusCode': '200',
                        'responseParameters':{
                            'method.response.header.Access-Control-Allow-Headers':"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                            'method.response.header.Access-Control-Allow-Origin':"'*'",
                            'method.response.header.Access-Control-Allow-Methods': "'GET,POST,PUT,DELETE,OPTIONS'"
                        }
                    }
                ],
                passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
                request_templates={"application/json":"{\"statusCode\":200}"}
            ),
            method_responses=[
                {
                    'statusCode': '200',
                    'responseParameters':{
                        'method.response.header.Access-Control-Allow-Headers': True,
                        'method.response.header.Access-Control-Allow-Methods': True,
                        'method.response.header.Access-Control-Allow-Origin': True,
                    }
                }
            ]
        )
