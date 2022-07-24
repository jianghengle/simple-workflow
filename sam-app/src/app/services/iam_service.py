import boto3
import json
import time

def create_platform_hosted_org_role(org_id, aws_region):
    iam = boto3.client('iam')

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": [
                    "dynamodb:*"
                ],
                "Resource": [
                    "arn:aws:dynamodb:" + aws_region + ":932651416286:table/" + org_id + "-*"
                ],
                "Effect": "Allow"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:CreateBucket",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::" + org_id + "-*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject"
                ],
                "Resource": [
                    "arn:aws:s3:::" + org_id + "-*"
                ]
            }
        ]
    }
    response = iam.create_policy(
        PolicyName=org_id+'-myworkflowhub-Policy',
        PolicyDocument=json.dumps(policy_document)
    )
    policy_arn = response['Policy']['Arn']
    waiter = iam.get_waiter('policy_exists')
    waiter.wait(PolicyArn=policy_arn)

    assume_role_policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "arn:aws:iam::932651416286:role/sam-app-MyAppFunctionRole-13502DH43K3Z7",
                        "arn:aws:iam::932651416286:user/dev"
                    ]
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    response = iam.create_role(
        RoleName=org_id+'-myworkflowhub-Role',
        AssumeRolePolicyDocument=json.dumps(assume_role_policy_document)
    )
    role_arn = response['Role']['Arn']
    waiter = iam.get_waiter('role_exists')
    waiter.wait(RoleName=org_id+'-myworkflowhub-Role')

    response = iam.attach_role_policy(RoleName=org_id+'-myworkflowhub-Role', PolicyArn=policy_arn)

    return role_arn