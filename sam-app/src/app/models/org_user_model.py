import time
import secrets
from .model import Model
from ..services import dynamo_service
from ..services import history_service
from .. import MyError


class OrgUserModel(Model):
    Fields = ['email', 'username', 'role', 'groups', 'activated', 'token', 'createdAt', 'updatedAt']

    def is_admin(self):
        return self.role == 'Owner' or self.role == 'Admin'

    def is_approved(self):
        return self.role and (not self.role == 'Pending Approval')

    def rotate_token(self, org_info):
        token = secrets.token_urlsafe()
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        dynamo_service.update_item(table, 'email', self.email, {'token': token})
        return token

    @staticmethod
    def get_all_by_org_info(org_info):
        if not org_info:
            raise MyError('Cannot find org_info from header')
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        items = dynamo_service.scan(table)
        return [OrgUserModel(item) for item in items]

    @staticmethod
    def get_by_email(org_info, email):
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        item = dynamo_service.get_item(table, 'email', email)
        if item:
            return OrgUserModel(item)
        return None

    @staticmethod
    def get_by_token(org_info):
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        items = dynamo_service.query(table, 'tokenIndex', 'token', org_info['orgUserToken'])
        if items and len(items) == 1:
            return OrgUserModel(items[0])
        return None

    @staticmethod
    def update_by_email(org_info, email, data, actor):
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        item = dynamo_service.get_item(table, 'email', email)
        org_user = OrgUserModel(item)
        if not org_user.token:
            org_user.rotate_token(org_info)
        timestamp = int(time.time()*1000)
        data['updatedAt'] = timestamp
        dynamo_service.update_item(table, 'email', email, data)
        item = dynamo_service.get_item(table, 'email', email)
        history_service.add_history(org_info, actor, 'Update', user_table_name + ':' + email, item)
        return OrgUserModel(item)

    @staticmethod
    def create(org_info, data, actor):
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        data['createdAt'] = timestamp
        data['updatedAt'] = timestamp
        dynamo_service.create_item(table, data, 'email')
        item = dynamo_service.get_item(table, 'email', data['email'])
        history_service.add_history(org_info, actor, 'Create', user_table_name + ':' + data['email'], item)
        return OrgUserModel(item)

    @staticmethod
    def delete(org_info, email, actor):
        user_table_name = org_info['userTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(user_table_name, aws_role, aws_region)
        history_service.add_history(org_info, actor, 'Delete', user_table_name + ':' + email, None)
        dynamo_service.delete_item(table, 'email', email)
