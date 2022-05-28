import uuid
import time
from ..models.org_user_model import OrgUserModel
from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from ..models.org_workflow_folder_model import OrgWorkflowFolderModel
from ..models.workflow_model import WorkflowModel
from .. import MyError
from ..services.ses_service import send_email

def get_workflows_in_folder(req, folder_id):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_config = OrgWorkflowConfigModel(req.body)
    #folder = OrgWorkflowFolderModel.get(req.org_info, folder_id)
    #workflow_config = OrgWorkflowConfigModel.get(req.org_info, folder.workflowConfigId)
    workflows = WorkflowModel.get_workflows_by_folder_id(req.org_info, workflow_config, folder_id)
    return [workflow.data for workflow in workflows]

def get_workflow(req, config_id, workflow_id):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_config = OrgWorkflowConfigModel(req.body)
    #workflow_config = OrgWorkflowConfigModel.get(req.org_info, config_id)
    workflow = WorkflowModel.get(req.org_info, workflow_config, workflow_id)
    return workflow.data

def create_workflow(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    data = req.body
    data['createdBy'] = req.org_user.email
    timestamp = int(time.time()*1000)
    data['createdAt'] = timestamp
    data['updatedAt'] = timestamp
    data['updatedBy'] = req.org_user.email
    folder = OrgWorkflowFolderModel.get(req.org_info, data['folderId'])
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, folder.workflowConfigId)
    data['id'] = str(workflow_config.increment_count(req.org_info))
    workflow = WorkflowModel.create(req.org_info, workflow_config, data)
    return workflow.data

def update_workflow(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    data = req.body
    timestamp = int(time.time()*1000)
    data['updatedAt'] = timestamp
    data['updatedBy'] = req.org_user.email
    folder = OrgWorkflowFolderModel.get(req.org_info, data['folderId'])
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, folder.workflowConfigId)
    workflow = WorkflowModel.update(req.org_info, workflow_config, data)
    return workflow.data

def delete_workflow(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    data = req.body
    folder = OrgWorkflowFolderModel.get(req.org_info, data['folderId'])
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, folder.workflowConfigId)
    WorkflowModel.delete(req.org_info, workflow_config, data['id'])
    return {'ok': True}

def send_email_about_workflow(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    email = req.org_user.email
    data = req.body
    receivers = data['receivers']
    workflow_id = data['workflowId']
    workflow_link = data['workflowLink']
    additional_message = data['additionalMessage']
    subject = EMAIL_SUBJECT.format(workflow_id)
    first_sentense = 'On behalf of User {}, myworkflowhub.com sent this message regarding the workflow {}: {}'.format(email, workflow_link, additional_message)
    
    body_text = EMAIL_BODY_TEXT.format(first_sentense, workflow_id, workflow_link)
    body_html = EMAIL_BODY_HTML.format(first_sentense, workflow_id, workflow_link)
    recipents = receivers
    send_email(recipents, subject, body_text, body_html)


EMAIL_SUBJECT = "Workflow {}"

EMAIL_BODY_TEXT = ("{}\r\n"
             "To see the workflow, please sign in https://myworkflowhub.com, and then go to "
             "workflows page and find the workflow by id({}). "
             "Or if you have already signed in with 'Remember me' option checked, "
             "you can open the following link directly.\r\n{}"
            )

EMAIL_BODY_HTML = """<html>
<body>
  <p>{}</p>
  <p>To see the workflow, please sign in https://myworkflowhub.com, and then go to workflow page and find the workflow by id({}).</p>
  <p>
    Or if you have already signed in with <em>Remember me</em> option checked, you can open the 
    <a href='{}' target="_blank">workflow link</a> directly.
  </p>
</body>
</html>
"""
