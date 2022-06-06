from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from ..models.org_workflow_folder_model import OrgWorkflowFolderModel
from ..models.workflow_model import WorkflowModel
from .. import MyError

def get_folders_for_workflow_config(req, workflow_config_id):
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, workflow_config_id)
    folders = OrgWorkflowFolderModel.get_by_workflow_config(req.org_info, workflow_config)
    return [folder.data for folder in folders]

def create_folder(req):
    data = req.body
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, data['workflowConfigId'])
    count = workflow_config.increment_count(req.org_info)
    new_id = data['workflowConfigId'] + '-' + str(count)
    data['id'] = new_id
    OrgWorkflowFolderModel.create_folder(req.org_info, data)
    folder = OrgWorkflowFolderModel.get(req.org_info, new_id)
    return folder.data

def update_folder(req):
    folder_id = req.body['id']
    OrgWorkflowFolderModel.update_folder(req.org_info, req.body)
    folder = OrgWorkflowFolderModel.get(req.org_info, folder_id)
    return folder.data

def delete_folder(req):
    data = req.body
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, data['workflowConfigId'])
    workflows = WorkflowModel.get_workflows_by_folder_id(req.org_info, workflow_config, data['id'])
    if len(workflows):
        raise MyError('Cannot delete folder having workflows.')
    folders = OrgWorkflowFolderModel.get_by_workflow_config(req.org_info, workflow_config)
    for folder in folders:
        if folder.parentId == data['id']:
            raise MyError('Cannot delete folder having sub-folder.')
    OrgWorkflowFolderModel.delete_folder(req.org_info, data['id'])
    return {'ok': True}
