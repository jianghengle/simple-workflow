import time
from .model import Model
from ..services import dynamo_service
from ..services import history_service
from .. import MyError


class WorkflowModel:
    CommonFields = ['id', 'folderId', 'state', 'createdBy', 'createdAt', 'updatedAt', 'updatedBy']

    def __init__(self, workflow_config, data={}):
        self.data = {}
        for field in self.CommonFields:
            value = data.get(field, None)
            self.data[field] = value
            setattr(self, field, value)
        for field in workflow_config.fields:
            name = field['name']
            value = data.get(name, None)
            self.data[name] = value
            setattr(self, name, value)
    

    @staticmethod
    def get_workflows_by_folder_id(org_info, workflow_config, folder_id):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = workflow_config.tableName
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        items = dynamo_service.query(table, 'folderIdIndex', 'folderId', folder_id)
        return [WorkflowModel(workflow_config, item) for item in items]

    @staticmethod
    def get(org_info, workflow_config, id):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = workflow_config.tableName
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        item = dynamo_service.get_item(table, 'id', id)
        return WorkflowModel(workflow_config, item)

    @staticmethod
    def create(org_info, workflow_config, data, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = workflow_config.tableName
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        data['createdAt'] = timestamp
        data['updatedAt'] = timestamp
        dynamo_service.create_item(table, data, 'id')
        item = dynamo_service.get_item(table, 'id', data['id'])
        history_service.add_history(org_info, actor, 'Create', table_name + ':' + data['id'], item)
        return WorkflowModel(workflow_config, item)

    @staticmethod
    def update(org_info, workflow_config, data, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = workflow_config.tableName
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        id = data['id']
        del data['id']
        timestamp = int(time.time()*1000)
        data['updatedAt'] = timestamp
        dynamo_service.update_item(table, 'id', id, data)
        item = dynamo_service.get_item(table, 'id', id)
        history_service.add_history(org_info, actor, 'Update', table_name + ':' + id, item)
        return WorkflowModel(workflow_config, item)

    @staticmethod
    def delete(org_info, workflow_config, id, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = workflow_config.tableName
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        dynamo_service.delete_item(table, 'id', id)
        history_service.add_history(org_info, actor, 'Delete', table_name + ':' + id, None)
