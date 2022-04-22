from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from ..models.org_workflow_folder_model import OrgWorkflowFolderModel
from ..models.workflow_model import WorkflowModel
from .. import MyError

def get_folders_for_workflow_config(req, workflow_config_id):
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, workflow_config_id)
    folders = OrgWorkflowFolderModel.get_by_workflow_config(req.org_info, workflow_config)
    return [folder.data for folder in folders]
