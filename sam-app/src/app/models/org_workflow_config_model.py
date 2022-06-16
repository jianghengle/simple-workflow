import time
from .model import Model
from .org_workflow_folder_model import OrgWorkflowFolderModel
from ..services import dynamo_service
from ..services import history_service
from .. import MyError


class OrgWorkflowConfigModel(Model):
    Fields = ['id', 'name', 'description', 'tableName', 'fields', 'states', 'userGroup', 'adminGroup', 'createdAt', 'updatedAt', 'updatedBy', 'isDeleted', 'count', 'creationNotifyingGroups', 'creationNotifyingOthers']

    def increment_count(self, org_info):
        table_name = org_info['workflowConfigTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        return dynamo_service.increment_attr(table, 'id', self.id, 'count')

    @staticmethod
    def get_all_by_org_info(org_info):
        if not org_info:
            raise MyError('Cannot find org_info from header')
        table_name = org_info['workflowConfigTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        items = dynamo_service.scan(table)
        return [OrgWorkflowConfigModel(item) for item in items]


    @staticmethod
    def create(user_email, org_info, data, actor):
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        workflow_table_name = data['tableName']
        try:
            create_workflow_table(aws_role, aws_region, workflow_table_name)
        except:
            raise MyError('Cannot create table with name: ' + workflow_table_name)
        
        workflow_config_table_name = org_info['workflowConfigTable']
        workflow_config_table = dynamo_service.get_table(workflow_config_table_name, aws_role, aws_region)
        items = dynamo_service.scan(workflow_config_table)
        workflow_configs = [OrgWorkflowConfigModel(item) for item in items]
        workflow_config_ids = [int(workflow_config.id) for workflow_config in workflow_configs]
        new_id = '1'
        if len(workflow_config_ids):
            new_id = str(max(workflow_config_ids) + 1)
        
        data['id'] = new_id
        timestamp = int(time.time()*1000)
        data['createdAt'] = timestamp
        data['updatedAt'] = timestamp
        data['updatedBy'] = user_email
        data['isDeleted'] = False
        dynamo_service.create_item(workflow_config_table, data, 'id')

        OrgWorkflowFolderModel.create_root_folder(org_info, new_id, user_email)

        item = dynamo_service.get_item(workflow_config_table, 'id', new_id)
        history_service.add_history(org_info, actor, 'Create', workflow_config_table_name + ':' + item['id'], item)
        return OrgWorkflowConfigModel(item)

    @staticmethod
    def update(user_email, org_info, id, data, actor):
        table_name = org_info['workflowConfigTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        data['updatedAt'] = timestamp
        data['updatedBy'] = user_email
        dynamo_service.update_item(table, 'id', id, data)
        item = dynamo_service.get_item(table, 'id', id)
        history_service.add_history(org_info, actor, 'Update', table_name + ':' + id, item)
        return OrgWorkflowConfigModel(item)

    @staticmethod
    def get(org_info, id):
        table_name = org_info['workflowConfigTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        item = dynamo_service.get_item(table, 'id', id)
        return OrgWorkflowConfigModel(item)

    @staticmethod
    def delete(user_email, org_info, id, actor):
        table_name = org_info['workflowConfigTable']
        aws_role = org_info['awsRole']
        aws_region = org_info['awsRegion']
        table = dynamo_service.get_table(table_name, aws_role, aws_region)
        timestamp = int(time.time()*1000)
        data = {
            'isDeleted': True,
            'updatedAt': timestamp,
            'updatedBy': user_email,
        }
        dynamo_service.update_item(table, 'id', id, data)
        item = dynamo_service.get_item(table, 'id', id)
        history_service.add_history(org_info, actor, 'Update', table_name + ':' + id, item)
        return OrgWorkflowConfigModel(item)
        

def create_workflow_table(aws_role, aws_region, table_name):
    attribute_definitions = [
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'folderId',
            'AttributeType': 'S'
        },
    ]
    key_schema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'
        },
    ]
    global_secondary_indexes=[
        {
            'IndexName': 'folderIdIndex',
            'KeySchema': [
                {
                    'AttributeName': 'folderId',
                    'KeyType': 'HASH'
                },
            ],
            'Projection': {
                'ProjectionType': 'ALL',
            },
        },
    ]
    dynamo_service.create_table(table_name, attribute_definitions, key_schema, global_secondary_indexes, aws_role, aws_region)
