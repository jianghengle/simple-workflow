from ..models.user_model import UserModel
from ..models.org_model import OrgModel
from ..models.org_user_model import OrgUserModel
from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from .. import MyError


def get_org(req, id):
    org = OrgModel.get_by_id(id)
    return org.data

def update_org(req, id):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if (not org_user) or (not org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    org = OrgModel.update(id, req.body)
    return org.data

def get_org_users(req):
    users = OrgUserModel.get_all_by_org_info(req.org_info)
    return [user.data for user in users]

def create_org_user(req):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if (not org_user) or (not org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)

    data = req.body
    user = UserModel.get_by_email(data['email'])
    if user and user.encryptedPassword:
        data['activated'] = True
    else:
        data['activated'] = False

    new_org_user = OrgUserModel.create(req.org_info, data)

    if not user:
        user = UserModel.create(data['email'])
    user.add_org_id(req.org_info['id'])
    return new_org_user.data

def update_org_user(req):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if (not org_user) or (not org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    user = OrgUserModel.update_by_email(req.org_info, req.body['email'], req.body['updates'])
    return user.data

def delete_org_user(req):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if (not org_user) or (not org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    OrgUserModel.delete(req.org_info, req.body['email'])
    user = UserModel.get_by_email(req.body['email'])
    user.remove_org_id(req.org_info['id'])
    return {'ok': True}

def get_org_workflow_configs(req):
    workflow_configs = OrgWorkflowConfigModel.get_all_by_org_info(req.org_info)
    ret = []
    for workflow_config in workflow_configs:
        if not workflow_config.isDeleted:
            ret.append(workflow_config.data)
    return ret

def create_workflow_config(req):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if not org_user.is_admin():
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.create(req.user.email, req.org_info, req.body)
    return workflow_config.data
    
def update_workflow_config(req, id):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if not org_user.is_admin():
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.update(req.user.email, req.org_info, id, req.body)
    return workflow_config.data

def get_workflow_config(req, id):
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, id)
    return workflow_config.data

def delete_workflow_config(req, id):
    org_user = OrgUserModel.get_by_email(req.org_info, req.user.email)
    if not org_user.is_admin():
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.delete(req.user.email, req.org_info, id)
    return workflow_config.data
