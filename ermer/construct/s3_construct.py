import os
import configparser
from aws_cdk import (
    aws_s3 as _s3,
    core
)

class S3Construct(core.Construct):

    def __init__(self,scope:core.Construct,id:str,Stage="default",**kwargs):
        super().__init__(scope, id, **kwargs)
        self.buckets = {}

        # create s3 bucket to store graph data

        self.ermer_bucket = _s3.Bucket(
            self,
            'ermer-graph-data',
        )
        
        # output s3 name 
        core.CfnOutput(
            self,
            "BucketName",
            value=self.ermer_bucket.bucket_name
        )

        self.buckets['ermer'] = self.ermer_bucket
        
    
    def get_s3_bucket(self,name):
        return self.buckets[name]
