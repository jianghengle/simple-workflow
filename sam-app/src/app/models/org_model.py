import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class OrgModel(Model):
    TableName = 'Orgs'
    Fields = ['id', 'name', 'awsRole', 'awsRegion', 'userTable', 'workflowConfigTable', 'folderTable', 's3Bucket', 'historyTable']

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(OrgModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return OrgModel(item)
        return None

    @staticmethod
    def update(id, data):
        table = dynamo_service.get_table(OrgModel.TableName)
        dynamo_service.update_item(table, 'id', id, data)
        return OrgModel(dynamo_service.get_item(table, 'id', id))

    @staticmethod
    def get_all():
        table = dynamo_service.get_table(OrgModel.TableName)
        items = dynamo_service.scan(table)
        return [OrgModel(item) for item in items]

    @staticmethod
    def create(org_id, org_name, aws_region, aws_role):
        table = dynamo_service.get_table(OrgModel.TableName)
        data = {
            'id': org_id,
            'awsRegion': aws_region,
            'awsRole': aws_role,
            'folderTable': org_id + '-Folders',
            'historyTable': org_id + '-History',
            'name': org_name,
            's3Bucket': org_id + '-workflows-bucket',
            'userTable': org_id + '-Users',
            'workflowConfigTable': org_id + '-WorkflowConfigs'
        }
        dynamo_service.create_item(table, data, 'id')
        item = dynamo_service.get_item(table, 'id', org_id)
        return OrgModel(item)
