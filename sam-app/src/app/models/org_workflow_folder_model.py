import time
from .model import Model
from ..services import dynamo_service
from ..services import history_service
from .. import MyError


class OrgWorkflowFolderModel(Model):
    Fields = ['id', 'workflowConfigId', 'parentId', 'name', 'description', 'createdAt', 'updatedAt']

    @staticmethod
    def create_root_folder(org_info, workflow_config_id, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        folder_table_name = org_info['folderTable']
        folder_table = dynamo_service.get_table(folder_table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        new_folder = {
            'id': workflow_config_id,
            'workflowConfigId': workflow_config_id,
            'parentId': None,
            'name': workflow_config_id + '_root',
            'description': None,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        dynamo_service.create_item(folder_table, new_folder, 'id')
        item = dynamo_service.get_item(folder_table, 'id', workflow_config_id)
        history_service.add_history(org_info, actor, 'Create', folder_table_name + ':' + workflow_config_id, item)

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
        items = dynamo_service.query(table, 'workflowConfigId-index', 'workflowConfigId', workflow_config.id)
        return [OrgWorkflowFolderModel(item) for item in items]

    @staticmethod
    def create_folder(org_info, new_folder, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        folder_table_name = org_info['folderTable']
        folder_table = dynamo_service.get_table(folder_table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        new_folder['createdAt'] = timestamp
        new_folder['updatedAt'] = timestamp
        dynamo_service.create_item(folder_table, new_folder, 'id')
        item = dynamo_service.get_item(folder_table, 'id', new_folder['id'])
        history_service.add_history(org_info, actor, 'Create', folder_table_name + ':' + new_folder['id'], item)

    @staticmethod
    def update_folder(org_info, data, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        folder_table_name = org_info['folderTable']
        folder_table = dynamo_service.get_table(folder_table_name, aws_role, aws_region)
        id = data['id']
        del data['id']
        timestamp = int(time.time()*1000)
        data['updatedAt'] = timestamp
        dynamo_service.update_item(folder_table, 'id', id, data)
        item = dynamo_service.get_item(folder_table, 'id', id)
        history_service.add_history(org_info, actor, 'Update', folder_table_name + ':' + id, item)
        return OrgWorkflowFolderModel(item)

    @staticmethod
    def delete_folder(org_info, id, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        folder_table_name = org_info['folderTable']
        folder_table = dynamo_service.get_table(folder_table_name, aws_role, aws_region)
        dynamo_service.delete_item(folder_table, 'id', id)
        history_service.add_history(org_info, actor, 'Delete', folder_table_name + ':' + id, None)
