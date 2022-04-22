import simplejson as json
import base64
from . import MyError
from .models.user_model import UserModel


class MyReq:
    def __init__(self, event):
        self.path = event['path']
        self.method = event['httpMethod']
        if self.method == 'OPTIONS':
            return

        self.body = event.get('body', None)
        if self.body:
            self.body = json.loads(self.body)
        self.headers = event.get('headers', {})
        self.queryStringParameters = event.get('queryStringParameters', {})
        self.requestContext = event.get('requestContext', None)
        self.user = None

        token = self.headers.get('Authorization', None)
        if self.method != 'OPTIONS' and token:
            self.user = UserModel.get_by_token(token)

        org_header = self.headers.get('my-org-info', None) or self.headers.get('My-Org-Info', None)
        if self.method != 'OPTIONS' and org_header:
            org_info_str = base64.b64decode(org_header.encode('utf-8')).decode('utf-8')
            self.org_info = json.loads(org_info_str)


def MyResp(data=None, code=200):
    return {
        "statusCode": code,
        "body": json.dumps(data),
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With, Origin, Accept, X-Token, X-AppToken, My-Org-Info',
            'Access-Control-Allow-Methods': 'PUT, GET, POST, DELETE, OPTIONS'
        },
    }
