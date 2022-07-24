import re, time
from ..models.user_model import UserModel
from ..models.org_model import OrgModel
from ..models.org_user_model import OrgUserModel
from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from .. import MyError
from ..services.s3_service import create_bucket
from ..services.ses_service import send_email
from ..services import dynamo_service
from ..services import iam_service


def get_org(req, id):
    user = req.org_user or req.user
    org = OrgModel.get_by_id(id)
    org_user = OrgUserModel.get_by_email(org.data, user.email)
    if (not org_user) or (not org_user.is_approved()):
        raise MyError('You are not in the org', 403)
    token = org_user.rotate_token(org.data)
    org.data['orgUserToken'] = token
    return org.data

def update_org(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    org = OrgModel.update(id, req.body)
    org.data['orgUserToken'] = req.org_user.token
    return org.data

def get_org_users(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    users = OrgUserModel.get_all_by_org_info(req.org_info)
    return [user.data for user in users]

def create_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    if (req.org_user.role == 'Owner'):
        if req.body['role'] not in ['Admin', 'User']:
            raise MyError('Incorrect org user role', 403)
    elif req.body['role'] != 'User':
        raise MyError('Incorrect org user role', 403)

    data = req.body
    user = UserModel.get_by_email(data['email'])
    if user and user.encryptedPassword:
        data['activated'] = True
    else:
        data['activated'] = False

    new_org_user = OrgUserModel.create(req.org_info, data, req.org_user.email)

    if not user:
        user = UserModel.create(data['email'])
    user.add_org_id(req.org_info['id'])
    return new_org_user.data

def update_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    user = OrgUserModel.update_by_email(req.org_info, req.body['email'], req.body['updates'], req.org_user.email)
    return user.data

def delete_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    OrgUserModel.delete(req.org_info, req.body['email'], req.org_user.email)
    user = UserModel.get_by_email(req.body['email'])
    user.remove_org_id(req.org_info['id'])
    return {'ok': True}

def approve_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)

    org_user = OrgUserModel.get_by_email(req.org_info, req.body['email'])
    if not org_user:
        raise MyError('Did not find org user ' + req.body['email'])
    if org_user.is_approved():
        raise MyError('The org user ' + req.body['email'] + ' has already been approved.')

    data = {'role': 'User', 'groups': []}

    user = UserModel.get_by_email(req.body['email'])
    if not user:
        user = UserModel.create(req.body['email'])

    user.add_org_id(req.org_info['id'])

    if user.encryptedPassword:
        data['activated'] = True
    else:
        data['activated'] = False

    org_user = OrgUserModel.update_by_email(req.org_info, req.body['email'], data, req.org_user.email)
    return org_user.data

def reject_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)

    org_user = OrgUserModel.get_by_email(req.org_info, req.body['email'])
    if not org_user:
        raise MyError('Did not find org user ' + req.body['email'])
    if org_user.is_approved():
        raise MyError('The org user ' + req.body['email'] + ' has already been approved.')

    OrgUserModel.delete(req.org_info, req.body['email'], req.org_user.email)
    return {'ok': True}

def get_org_workflow_configs(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_configs = OrgWorkflowConfigModel.get_all_by_org_info(req.org_info)
    ret = []
    for workflow_config in workflow_configs:
        if not workflow_config.isDeleted:
            ret.append(workflow_config.data)
    return ret

def create_workflow_config(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.create(req.org_user.email, req.org_info, req.body, req.org_user.email)
    return workflow_config.data
    
def update_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.update(req.org_user.email, req.org_info, id, req.body, req.org_user.email)
    return workflow_config.data

def get_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, id)
    return workflow_config.data

def delete_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.delete(req.org_user.email, req.org_info, id, req.org_user.email)
    return workflow_config.data


def check_org_id(req):
    orgs = OrgModel.get_all()
    for org in orgs:
        if org.id == req.body['orgId']:
            raise MyError('This org id has already been used', 403)
    return {'ok': True}

def create_org(req):
    org_id = req.body['orgId']
    if not re.match("^([a-z]|[0-9])+$", org_id):
        raise MyError('This org id is invalid', 403)
    orgs = OrgModel.get_all()
    for org in orgs:
        if org.id == req.body['orgId']:
            raise MyError('This org id has already been used', 403)
    org_name = req.body['orgName']
    aws_region = req.body['awsRegion']
    aws_role = req.body['iamRole']
    create_org_tables(org_id, aws_role, aws_region)
    create_org_s3_bucket(org_id, aws_role)

    org = OrgModel.create(org_id, org_name, aws_region, aws_role)
    user = UserModel.get_by_token(req.token)
    org_user_data = {
        'email': user.email,
        'activated': True,
        'groups': [],
        'role': 'Owner',
        'username': user.username,
    }
    org_user = OrgUserModel.create(org.data, org_user_data, user.email)
    user.add_org_id(org_id)
    my_notice = 'myworkflowhub new org created: ' + org_id + '<' + user.email + '>'
    send_email(['jianghengle@gmail.com'], my_notice, my_notice, my_notice)

def create_role_for_platform_hosted_org(req):
    org_id = req.body['orgId']
    if not re.match("^([a-z]|[0-9])+$", org_id):
        raise MyError('This org id is invalid', 403)
    orgs = OrgModel.get_all()
    for org in orgs:
        if org.id == req.body['orgId']:
            raise MyError('This org id has already been used', 403)
    aws_role = iam_service.create_platform_hosted_org_role(org_id, 'us-west-2')
    time.sleep(20)
    return {'awsRole': aws_role}


FolderTableAttr = [
    { 'AttributeName': 'id', 'AttributeType': 'S'},
    { 'AttributeName': 'workflowConfigId', 'AttributeType': 'S'},
]
FolderTableKey = [
    { 'AttributeName': 'id', 'KeyType': 'HASH'},
]
FolderTableGSI = [
    {
        'IndexName': 'workflowConfigId-index',
        'KeySchema': [
            { 'AttributeName': 'workflowConfigId', 'KeyType': 'HASH' },
        ],
        'Projection': { 'ProjectionType': 'ALL' },
    },
]

HistoryTableAttr = [
    { 'AttributeName': 'id', 'AttributeType': 'S'},
    { 'AttributeName': 'entityId', 'AttributeType': 'S'},
    { 'AttributeName': 'timestamp', 'AttributeType': 'N'},
]
HistoryTableKey = [
    { 'AttributeName': 'id', 'KeyType': 'HASH'},
]
HistoryTableGSI = [
    {
        'IndexName': 'entityId-timestamp-index',
        'KeySchema': [
            { 'AttributeName': 'entityId', 'KeyType': 'HASH' },
            { 'AttributeName': 'timestamp', 'KeyType': 'RANGE' },
        ],
        'Projection': { 'ProjectionType': 'ALL' },
    },
]

UserTableAttr = [
    { 'AttributeName': 'email', 'AttributeType': 'S'},
    { 'AttributeName': 'token', 'AttributeType': 'S'},
]
UserTableKey = [
    { 'AttributeName': 'email', 'KeyType': 'HASH'},
]
UserTableGSI = [
    {
        'IndexName': 'tokenIndex',
        'KeySchema': [
            { 'AttributeName': 'token', 'KeyType': 'HASH' },
        ],
        'Projection': { 'ProjectionType': 'ALL' },
    },
]

WorkflowConfigTableAttr = [
    { 'AttributeName': 'id', 'AttributeType': 'S'},
]
WorkflowConfigTableKey = [
    { 'AttributeName': 'id', 'KeyType': 'HASH'},
]


def create_org_tables(org_id, aws_role, aws_region):
    dynamo_service.create_table(org_id + '-Users', UserTableAttr, UserTableKey, UserTableGSI, aws_role, aws_region)
    dynamo_service.create_table(org_id + '-Folders', FolderTableAttr, FolderTableKey, FolderTableGSI, aws_role, aws_region)
    dynamo_service.create_table(org_id + '-History', HistoryTableAttr, HistoryTableKey, HistoryTableGSI, aws_role, aws_region)
    dynamo_service.create_table(org_id + '-WorkflowConfigs', WorkflowConfigTableAttr, WorkflowConfigTableKey, [], aws_role, aws_region)

def create_org_s3_bucket(org_id, aws_role):
    create_bucket(org_id + '-workflows-bucket', aws_role)


My_managed_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "RESOURCE_ARN"
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:DeleteItem",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
            ],
            "Resource": "RESOURCE_ARN"
        }
    ]
}
