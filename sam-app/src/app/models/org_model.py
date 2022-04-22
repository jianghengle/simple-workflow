import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class OrgModel(Model):
    TableName = 'Orgs'
    Fields = ['id', 'name', 'awsRole', 'awsRegion', 'userTable', 'workflowConfigTable', 'folderTable', 's3Bucket']

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(OrgModel.TableName)
        return OrgModel(dynamo_service.get_item(table, 'id', id))

    @staticmethod
    def update(id, data):
        table = dynamo_service.get_table(OrgModel.TableName)
        dynamo_service.update_item(table, 'id', id, data)
        return OrgModel(dynamo_service.get_item(table, 'id', id))
