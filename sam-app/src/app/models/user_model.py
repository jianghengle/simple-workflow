import bcrypt
import string
import secrets
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class UserModel(Model):
    TableName = 'MyUsers'
    TokenGSI = ('tokenGSI', 'token')
    Fields = ['email', 'username', 'encryptedPassword', 'token', 'orgIds', 'resetPasswordToken', 'updatedAt']

    def update_username(self, username):
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'email', self.email, {'username': username})
        return UserModel(dynamo_service.get_item(table, 'email', self.email))

    def add_org_id(self, org_id):
        table = dynamo_service.get_table(UserModel.TableName)
        self.orgIds.append(org_id)
        dynamo_service.update_item(table, 'email', self.email, {'orgIds': self.orgIds})

    def remove_org_id(self, org_id):
        table = dynamo_service.get_table(UserModel.TableName)
        self.orgIds.remove(org_id)
        dynamo_service.update_item(table, 'email', self.email, {'orgIds': self.orgIds})

    @staticmethod
    def get_by_token(token):
        if not token:
            raise MyError('No token')
        table = dynamo_service.get_table(UserModel.TableName)
        items = dynamo_service.query(table, UserModel.TokenGSI[0], UserModel.TokenGSI[1], token)
        if not len(items):
            return None
        if len(items) > 1:
            print('Found multiple users with same token')
            return None
        return UserModel(items[0])

    @staticmethod
    def generate_password_reset_token(email):
        table = dynamo_service.get_table(UserModel.TableName)
        user = UserModel(dynamo_service.get_item(table, 'email', email))
        token = secrets.token_urlsafe()
        dynamo_service.update_item(table, 'email', email, { 'resetPasswordToken': token, 'updatedAt': int(time.time()*1000) })
        return UserModel(dynamo_service.get_item(table, 'email', email))

    @staticmethod
    def reset_password(email, password, token):
        table = dynamo_service.get_table(UserModel.TableName)
        user = UserModel(dynamo_service.get_item(table, 'email', email))
        if not user.resetPasswordToken:
            raise MyError('Password reset token not set.')
        if user.resetPasswordToken != token:
            raise MyError('Invalid token.')
        if user.encryptedPassword and (int(time.time()*1000) - user.updatedAt) > (3600 * 3000):
            raise MyError('Token expired.')
        encrypted_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        alphabet = string.ascii_letters + string.digits
        new_token = ''.join(secrets.choice(alphabet) for i in range(64))
        dynamo_service.update_item(table, 'email', email, { 'encryptedPassword': encrypted_password, 'token': new_token, 'resetPasswordToken': '', 'updatedAt': int(time.time()*1000) })
        return UserModel(dynamo_service.get_item(table, 'email', email))

    @staticmethod
    def auth_user(email, password):
        table = dynamo_service.get_table(UserModel.TableName)
        user = UserModel(dynamo_service.get_item(table, 'email', email))
        if not user.encryptedPassword:
            raise MyError('Password not set.', 403)
        if bcrypt.checkpw(password.encode('utf-8'), user.encryptedPassword.encode('utf-8')):
            return user
        raise MyError('Failed to authenticate user.', 403)

    @staticmethod
    def get_by_email(email):
        table = dynamo_service.get_table(UserModel.TableName)
        item = dynamo_service.get_item(table, 'email', email)
        if item:
            return UserModel(item)
        return None

    @staticmethod
    def create(email):
        table = dynamo_service.get_table(UserModel.TableName)
        alphabet = string.ascii_letters + string.digits
        new_token = ''.join(secrets.choice(alphabet) for i in range(64))
        dynamo_service.create_item(table, {'email': email, 'token': new_token, 'orgIds': [], 'updatedAt': int(time.time()*1000)}, 'email')
        item = dynamo_service.get_item(table, 'email', email)
        return UserModel(item)
