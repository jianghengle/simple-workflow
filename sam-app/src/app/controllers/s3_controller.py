import os, random, string
from ..services.s3_service import create_presigned_post, create_presigned_url

def get_s3_upload_url(req):
    filename = req.body['filename']
    name, ext = os.path.splitext(filename)
    key = 'uploaded_files/' + name + '.' + get_random_string(8) + ext
    s3_bucket = req.org_info['s3Bucket']
    url = create_presigned_post(s3_bucket, key, role=req.org_info['awsRole'])
    url['bucket'] = s3_bucket
    url['key'] = key
    url['filename'] = filename
    return url

def get_s3_download_url(req):
    bucket = req.body['bucket']
    key = req.body['key']
    url = create_presigned_url(bucket, key, role=req.org_info['awsRole'])
    return {'url': url}

def get_random_string(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))

