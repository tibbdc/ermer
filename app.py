#!/usr/bin/env python3
import os

from aws_cdk import core as cdk
from aws_cdk import core

from ermer.stack.ermer_stack import ErmerStack


app = core.App()


STACK_NAME ="ermer"
STAGE="prod"
env_us = core.Environment(account=os.environ["AccountID"], region=os.environ["Region"])

ErmerStack(
    app, 
    STACK_NAME+"-"+STAGE,
    env=env_us,
    Stage=STAGE  
    )

app.synth()
