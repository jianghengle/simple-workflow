import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class OrgWorkflowFolderModel(Model):
    Fields = ['id', 'workflowConfigId', 'parentId', 'name', 'description']

    @staticmethod
    def create_root_folder(org_info, workflow_config_id):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        folder_table_name = org_info['folderTable']
        folder_table = dynamo_service.get_table(folder_table_name, aws_role, aws_region)
        new_folder = {
            'id': workflow_config_id,
            'workflowConfigId': workflow_config_id,
            'parentId': None,
            'name': workflow_config_id + '_root',
            'description': None,
        }
        dynamo_service.create_item(folder_table, new_folder, 'id')

    @staticmethod
    def get(org_info, id):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = org_info['folderTable']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        item = dynamo_service.get_item(table, 'id', id)
        return OrgWorkflowFolderModel(item)

    @staticmethod
    def get_by_workflow_config(org_info, workflow_config):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table_name = org_info['folderTable']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        items = dynamo_service.query(table, 'workflowConfigIdIndex', 'workflowConfigId', workflow_config.id)
        return [OrgWorkflowFolderModel(item) for item in items]
