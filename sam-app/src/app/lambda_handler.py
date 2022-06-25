from . import MyError
from .my_http import MyReq, MyResp
from .controllers import user_controller
from .controllers import org_controller
from .controllers import workflow_controller
from .controllers import folder_controller
from .controllers import s3_controller


class MyRouter:
    def __init__(self, path_handlers):
        self.path_handlers = path_handlers

    def route(self, req):
        req_method = req.method
        if req_method == 'OPTIONS':
            return MyResp()

        req_path_parts = self.split_path(req.path)
        for (method, path, auth_required, handler) in self.path_handlers:
            if req_method != method:
                continue
            (match, params) = self.path_match(req_path_parts, self.split_path(path))
            if match:
                if auth_required and (not req.user) and (not req.org_user):
                    raise MyError('Failed to authenticate the user', 403)
                return MyResp(handler(req, *params))
        raise MyError('Did not find the handler', 404)

    def path_match(self, req_path_parts, handler_path_parts):
        params = []
        if len(req_path_parts) != len(handler_path_parts):
            return (False, None)
        for i in range(len(req_path_parts)):
            req_path_part = req_path_parts[i]
            handler_path_part = handler_path_parts[i]
            if handler_path_part.startswith(':'):
                params.append(req_path_part)
            elif handler_path_part != req_path_part:
                return (False, None)
        return (True, tuple(params))

    def split_path(self, path):
        parts = []
        for s in path.split('/'):
            part = s.strip()
            if part:
                parts.append(part)
        return parts



def handle(event, context):
    try:
        req = MyReq(event)
        router = MyRouter([
            ('GET', '/user/get-user', True, user_controller.get_user),
            ('POST', '/user/update-username', True, user_controller.update_username),
            ('POST', '/user/request-to-join-org', False, user_controller.request_to_join_org),
            ('POST', '/user/generate-password-reset-token', False, user_controller.generate_password_reset_token),
            ('POST', '/user/send-invite', True, user_controller.send_invite),
            ('POST', '/user/reset-password', False, user_controller.reset_password),
            ('POST', '/user/sign-up', False, user_controller.sign_up),
            ('POST', '/user/auth-user', False, user_controller.auth_user),
            ('GET', '/org/get-org/:id', True, org_controller.get_org),
            ('POST', '/org/update-org/:id', True, org_controller.update_org),
            ('GET', '/org/get-org-users', True, org_controller.get_org_users),
            ('POST', '/org/create-org-user', True, org_controller.create_org_user),
            ('POST', '/org/update-org-user', True, org_controller.update_org_user),
            ('POST', '/org/delete-org-user', True, org_controller.delete_org_user),
            ('POST', '/org/approve-org-user', True, org_controller.approve_org_user),
            ('POST', '/org/reject-org-user', True, org_controller.reject_org_user),
            ('GET', '/org/get-org-workflow-configs', True, org_controller.get_org_workflow_configs),
            ('POST', '/org/create-workflow-config', True, org_controller.create_workflow_config),
            ('POST', '/org/update-workflow-config/:id', True, org_controller.update_workflow_config),
            ('GET', '/org/get-org-workflow-config/:id', True, org_controller.get_workflow_config),
            ('POST', '/org/delete-workflow-config/:id', True, org_controller.delete_workflow_config),
            ('POST', '/org/get-org-workflows-in-folder/:folder_id', True, workflow_controller.get_workflows_in_folder),
            ('POST', '/org/get-workflow/:config_id/:workflow_id', True, workflow_controller.get_workflow),
            ('POST', '/org/create-workflow', True, workflow_controller.create_workflow),
            ('POST', '/org/update-workflow', True, workflow_controller.update_workflow),
            ('POST', '/org/delete-workflow', True, workflow_controller.delete_workflow),
            ('POST', '/org/move-workflow', True, workflow_controller.move_workflow),
            ('POST', '/org/send-email-about-workflow', True, workflow_controller.send_email_about_workflow),
            ('GET', '/org/get-folders-for-workflow-config/:config_id', True, folder_controller.get_folders_for_workflow_config),
            ('POST', '/org/create-folder', True, folder_controller.create_folder),
            ('POST', '/org/update-folder', True, folder_controller.update_folder),
            ('POST', '/org/delete-folder', True, folder_controller.delete_folder),
            ('POST', '/org/get-s3-upload-url', True, s3_controller.get_s3_upload_url),
            ('POST', '/org/get-s3-download-url', True, s3_controller.get_s3_download_url),
        ])
        return router.route(req)
    except MyError as err:
        print('MyError: ' + err.message )
        return MyResp({ 'err': err.message }, err.code)
    except Exception as e:
        print(e)
        return MyResp({ 'err': str(e) }, 500)
