from ..models.user_model import UserModel
from ..models.org_model import OrgModel
from ..models.org_user_model import OrgUserModel
from ..models.org_workflow_config_model import OrgWorkflowConfigModel
from .. import MyError


def get_org(req, id):
    user = req.org_user or req.user
    org = OrgModel.get_by_id(id)
    org_user = OrgUserModel.get_by_email(org.data, user.email)
    if (not org_user) or (not org_user.is_approved()):
        raise MyError('You are not in the org', 403)
    token = org_user.rotate_token(org.data)
    org.data['orgUserToken'] = token
    return org.data

def update_org(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    org = OrgModel.update(id, req.body)
    org.data['orgUserToken'] = req.org_user.token
    return org.data

def get_org_users(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    users = OrgUserModel.get_all_by_org_info(req.org_info)
    return [user.data for user in users]

def create_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
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
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    user = OrgUserModel.update_by_email(req.org_info, req.body['email'], req.body['updates'])
    return user.data

def delete_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)
    OrgUserModel.delete(req.org_info, req.body['email'])
    user = UserModel.get_by_email(req.body['email'])
    user.remove_org_id(req.org_info['id'])
    return {'ok': True}

def approve_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)

    org_user = OrgUserModel.get_by_email(req.org_info, req.body['email'])
    if not org_user:
        raise MyError('Did not find org user ' + req.body['email'])
    if org_user.is_approved():
        raise MyError('The org user ' + req.body['email'] + ' has already been approved.')

    data = {'role': 'User', 'groups': []}

    user = UserModel.get_by_email(req.body['email'])
    if not user:
        user = UserModel.create(req.body['email'])

    user.add_org_id(req.org_info['id'])

    if user.encryptedPassword:
        data['activated'] = True
    else:
        data['activated'] = False

    org_user = OrgUserModel.update_by_email(req.org_info, req.body['email'], data)
    return org_user.data

def reject_org_user(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('Did not find org user or org user is not admin', 403)

    org_user = OrgUserModel.get_by_email(req.org_info, req.body['email'])
    if not org_user:
        raise MyError('Did not find org user ' + req.body['email'])
    if org_user.is_approved():
        raise MyError('The org user ' + req.body['email'] + ' has already been approved.')

    OrgUserModel.delete(req.org_info, req.body['email'])
    return {'ok': True}

def get_org_workflow_configs(req):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_configs = OrgWorkflowConfigModel.get_all_by_org_info(req.org_info)
    ret = []
    for workflow_config in workflow_configs:
        if not workflow_config.isDeleted:
            ret.append(workflow_config.data)
    return ret

def create_workflow_config(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.create(req.org_user.email, req.org_info, req.body)
    return workflow_config.data
    
def update_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.update(req.org_user.email, req.org_info, id, req.body)
    return workflow_config.data

def get_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_approved()):
        raise MyError('You are not allow to see this org', 403)
    workflow_config = OrgWorkflowConfigModel.get(req.org_info, id)
    return workflow_config.data

def delete_workflow_config(req, id):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    workflow_config = OrgWorkflowConfigModel.delete(req.org_user.email, req.org_info, id)
    return workflow_config.data
