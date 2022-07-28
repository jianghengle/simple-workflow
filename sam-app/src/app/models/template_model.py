import time
from .model import Model
from ..services import dynamo_service
from ..services import history_service
from .. import MyError


class TemplateModel(Model):
    TableName = 'WorkflowConfigTemplates'
    Fields = ['id', 'name', 'description', 'workflowConfig']

    @staticmethod
    def get_all():
        table = dynamo_service.get_table(TemplateModel.TableName)
        items = dynamo_service.scan(table)
        return [TemplateModel(item) for item in items]

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(TemplateModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return TemplateModel(item)
        return None
