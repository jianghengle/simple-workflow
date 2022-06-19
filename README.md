# simple-workflow

## Introduction

The [myworkflowhub.com](https://myworkflowhub.com/) is a free configurable workflow management platform. With minimum efforts, you could have your collabrative workflows for your organiaztion (like invoices management) set up, as shown in the screen shots below:

![dashboard](https://github.com/jianghengle/simple-workflow/raw/main/screenshots/dashboard.png)

![edit](https://github.com/jianghengle/simple-workflow/raw/main/screenshots/edit.png)

The workflows are totaly customerized by yourself including:
- what fields should be in a workflow
- what states can a workflow go through and their transitions
- the user's permissions on the workflow in each state.
- and more

You can play with the app by login [myworkflowhub.com](https://myworkflowhub.com/) with a demo user `demo@myworkflowhub.com` and password `123456`, where you can create/edit workflows or even new workflow config.

## Tech stack

The backend in the `sam-app` folder is a [AWS SAM app](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) on AWS infrastructure using API gateway, lambda and DynamoDB.

The frontend in the `client` folder is a [Vue app](https://vuejs.org/) distributed by AWS Cloudfront backed on S3 bucket

The tenants' data are hosted in their individual AWS accounts securely and seperately, while the our platform is serving them just by assuming an IAM role.
