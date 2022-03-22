
# ERMer: A serverless platform for navigating, analyzing, and visualizing Escherichiacoli regulatory landscape through graph database

The code of paper 'ERMer: A serverless platform for navigating, analyzing, and visualizing Escherichiacoli regulatory landscape through graph database', here we provide our backend demo code that how to quickly deploy the resources on AWS, and how to implement our business logic. 

## Introduction

This project is developed by using [AWS CDK](https://aws.amazon.com/cdk/), and all the cloud application resources are defined by using python language. 

+   ermer: all the application resources definitions

+   lambda: our demo business logic, how to use gremlin api to query data in python

+   notebook: the demo code for connecting the AWS Neptune, and the Neptune loader command for loading data from external files directly into a Neptune DB instance. We recommend you that use AWS SageMaker to set up with [Neptune Jupyter notebooks](https://docs.aws.amazon.com/neptune/latest/userguide/graph-notebooks.html).

+   graph_data: demo graph data in gremlin format, which will be uploaded to your s3 bucket.

## Installation & Deployment 

### Installation

AWS CDK uses specific versions Node.js (>=10.13.0, except for version 13.0.0 - 13.6.0). A version in active long-term support (LTS) is recommended.

+   To install node.js, please folow the official instructions node.js website and follow the instructions for your given operating system.
+   If you already have node.js installed, verify which version you have by running:

```
node --version
```

To use Python as your CDK language of choice, you will need to have Python installed. Specifically you will need Python 3.6 or later installed. You can find information on installing Python [here](https://www.python.org/downloads/).

```
python --version
```

To install the AWS CDK CLI, you need to first have the Node Package Manager (npm) installed. Install the AWS CDK CLI globally by running the following command:

```
npm install -g aws-cdk

# verify

cdk --version
```

To deploy our demo project, please use git to clone our project:

```
git clone https://github.com/tibbdc/ermer
```

To make sure that you have the credentials to interact with [AWS](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).

```
aws configure
```

### Deployment

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

```
# add your aws accountID
$ export AccoundID="{your_aws_accountid}"

# add your deploy region
$ export Region="{your_deployed_region}"

# deploy project
$ cdk deploy
```

To deploy the all application resources on AWS.

### Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation
 * `cdk destroy`    delete the deployed stack   

### Output

After you deploy the stack, you will get the following resources:

``` python
ermer-prod.apigatewayconstructermerEndpoint* = "{your_apigteway_endpoint}"
ermer-prod.neptuneconstructNeptuneClusterEndpoints* = "{your_cluster_endpoint}"
ermer-prod.neptuneconstructNeptuneRoleArn* = "{your_neptune_assumed_role}"
ermer-prod.s3constructBucketName* = "{your_s3_bucket}"


```

### Attentions

If you don't need the application stack any more, please delete the resources on aws, use command `cdk destroy` or login the aws [cloudformation](https://us-east-1.console.aws.amazon.com/cloudformation/).

## Stack

This stack contains the resources below:

+   S3: Amazon S3 is cloud object storage with industry-leading scalability, data availability, security, and performance.

+   API Gateway: Amazon API Gateway is a fully managed service that makes it easy for developers to create, publish, maintain, monitor, and secure APIs at any scale.

+   Lambda: Lambda is a compute service that lets you run code without provisioning or managing servers. Lambda runs your code on a high-availability compute infrastructure and performs all of the administration of the compute resources, including server and operating system maintenance, capacity provisioning and automatic scaling, code monitoring and logging. 

+   Neptune: Amazon Neptune is a fast, reliable, fully managed graph database service that makes it easy to build and run applications.

## License Summary

This sample code is made available under the Apache license. See the LICENSE file.