import time
import uuid
from decimal import Decimal
from . import dynamo_service

def add_history(org_info, actor, action, entity_id, entity_data):
    aws_role = org_info['awsRole']
    aws_region = org_info['awsRegion']
    table_name = org_info.get('historyTable', '')
    if not table_name:
        return
    table = dynamo_service.get_table(table_name, aws_role, aws_region)
    if entity_data:
        timestamp = Decimal(entity_data['updatedAt'] / 1000)
    else:
        timestamp = Decimal(time.time())

    data = {
        'id': str(uuid.uuid4()),
        'entityId': entity_id,
        'entityData': entity_data,
        'timestamp': timestamp,
        'actor': actor,
        'action': action
    }
    dynamo_service.create_item(table, data, 'id')
