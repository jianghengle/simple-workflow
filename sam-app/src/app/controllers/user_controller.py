from ..models.user_model import UserModel
from ..models.org_model import OrgModel
from ..models.org_user_model import OrgUserModel
from urllib.parse import quote
from ..services.ses_service import send_email
from .. import MyError

def get_user(req):
    return {
        'email': req.user.email,
        'username': req.user.username,
        'hasPassword': bool(req.user.encryptedPassword),
        'orgIds': req.user.orgIds,
    }

def update_username(req):
    user = UserModel.get_by_token(req.token)
    user = user.update_username(req.body['username'])
    try:
        for org_id in user.orgIds:
            org = OrgModel.get_by_id(org_id)
            org_user = OrgUserModel.get_by_email(org.data, user.email)
            if org_user:
                OrgUserModel.update_by_email(org.data, user.email, {'username': user.username}, user.email)
    except:
        print('failed to update org user username: ' + user.email)
    return {
        'email': user.email,
        'username': user.username,
        'hasPassword': bool(user.encryptedPassword),
        'orgIds': user.orgIds,
    }

def request_to_join_org(req):
    org_id = req.body['orgId']
    org = OrgModel.get_by_id(org_id)
    if not org:
        raise MyError('The org id does NOT exist.', 403)
    email = req.body['email']
    org_user = OrgUserModel.get_by_email(org.data, email)
    if org_user:
        if org_user.role == 'Pending Approval':
            raise MyError('You have requested the org. The admin is reviewing your request.', 403)
        else:
            raise MyError('You are already in the org. If you have not set your password, you want to ask the admin to send you the invition link.', 403)
    data = {'email': req.body['email'], 'username': req.body['username'], 'role': 'Pending Approval'}
    new_org_user = OrgUserModel.create(org.data, data, data['email'])
    return {'ok': True}

def generate_password_reset_token(req):
    email = req.body['email']
    user = UserModel.generate_password_reset_token(email)
    password_reset_link = 'https://myworkflowhub.com/user/change-password/' +  quote(user.email, safe='') + '/' + user.resetPasswordToken + '/reset'
    body_text = RESET_TEXT.format(password_reset_link)
    body_html = RESET_HTML.format(password_reset_link, password_reset_link)
    recipents = [email]
    send_email(recipents, RESET_SUBJECT, body_text, body_html)
    return {'ok': True}

def send_invite(req):
    if (not req.org_user) or (not req.org_user.is_admin()):
        raise MyError('You are not admin', 403)
    email = req.body['email']
    user = UserModel.get_by_email(email)
    if user.encryptedPassword:
        raise MyError('User has been activated.')
    user = UserModel.generate_password_reset_token(email)
    password_reset_link = 'https://myworkflowhub.com/user/change-password/' +  quote(user.email, safe='') + '/' + user.resetPasswordToken + '/new'
    request_user = str(req.org_user.username) + '<' + req.org_user.email + '>'
    org = OrgModel.get_by_id(req.org_info['id'])
    org_name = org.name
    body_text = INVITE_TEXT.format(request_user, org_name, password_reset_link)
    body_html = INVITE_HTML.format(request_user, org_name, password_reset_link, password_reset_link)
    recipents = [email]
    send_email(recipents, INVITE_SUBJECT, body_text, body_html)
    return {'ok': True}

def reset_password(req):
    email = req.body['email']
    password = req.body['password']
    token = req.body['token']
    user = UserModel.reset_password(email, password, token)
    if 'username' in req.body:
        user.update_username(req.body['username'])
    try:
        for org_id in user.orgIds:
            org = OrgModel.get_by_id(org_id)
            org_user = OrgUserModel.get_by_email(org.data, email)
            if org_user:
                data = {'activated': True}
                if 'username' in req.body:
                    data['username'] = req.body['username']
                OrgUserModel.update_by_email(org.data, email, data, email)
    except:
        print('failed to activate org user: ' + email)
    return {'ok': True}

def sign_up(req):
    email = req.body['email']
    user = UserModel.get_by_email(email)
    if user:
        raise MyError('The email address has been already used', 403)
    UserModel.create(email)
    user = UserModel.generate_password_reset_token(email)
    password_reset_link = 'https://myworkflowhub.com/user/change-password/' +  quote(email, safe='') + '/' + user.resetPasswordToken + '/new'
    body_text = SIGN_UP_TEXT.format(password_reset_link)
    body_html = SIGN_UP_HTML.format(password_reset_link, password_reset_link)
    recipents = [email]
    send_email(recipents, SIGN_UP_SUBJECT, body_text, body_html)
    my_notice = 'myworkflowhub new sign up: ' + email
    send_email(['jianghengle@gmail.com'], my_notice, my_notice, my_notice)
    return {'ok': True}

def auth_user(req):
    email = req.body['email']
    password = req.body['password']
    user = UserModel.auth_user(email, password)
    return {
        'email': user.email,
        'username': user.username,
        'token': user.token,
        'orgIds': user.orgIds,
    }


RESET_SUBJECT = "myworkflowhub.com Password Reset"

RESET_TEXT = "Please use the following link to change your password:\r\n{}"

RESET_HTML = """<html>
<body>
  <p>Please use the following link to change your password:</p>
  <p><a href='{}' target="_blank">{}</a></p>
</body>
</html>
"""

INVITE_SUBJECT = "myworkflowhub.com invite"

INVITE_TEXT = "Hi, {} invited you to join the org \"{}\". Please use the following link to set your password:\r\n{}, and then sign in https://myworkflowhub.com"

INVITE_HTML = """<html>
<body>
  <p>Hi, {} invited you to join the org \"{}\". Please use the following link to set your password:</p>
  <p><a href='{}' target="_blank">{}</a></p>
  <p>and then you can sign in https://myworkflowhub.com.</p>
</body>
</html>
"""

SIGN_UP_SUBJECT = "myworkflowhub.com Sign Up"

SIGN_UP_TEXT = "Hi, you have requested to sign up myworkflowhub.com. Please use the following link to set your password:\r\n{}, and then sign in https://myworkflowhub.com"

SIGN_UP_HTML = """<html>
<body>
  <p>Hi, you have requested to sign up myworkflowhub.com. Please use the following link to set your password:</p>
  <p><a href='{}' target="_blank">{}</a></p>
  <p>and then you can sign in https://myworkflowhub.com.</p>
</body>
</html>
"""
