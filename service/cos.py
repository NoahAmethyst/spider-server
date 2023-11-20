import logging
import os

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client


class CosCli:
    _instance = None

    def __init__(self):
        self.secret_id = os.environ('TC_SECRET_ID')
        self.secret_key = os.environ('TC_SECRET_KEY')
        self.region = 'ap-nanjing'
        self.bucket = 'bot-1317156498'

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(CosCli, cls).__new__(cls, *args, **kwargs)
            cls._instance.secret_id = os.environ('TC_SECRET_ID')
            cls._instance.secret_key = os.environ('TC_SECRET_KEY')
            cls._instance.region = 'ap-nanjing'
            cls._instance.bucket = 'bot-1317156498'
        return cls._instance

    def upload_file(self, cos_path, cos_name, file_path):
        config = CosConfig(Region=self.region, SecretId=self.secret_id, SecretKey=self.secret_key, Token=None,
                           Domain=None)
        client = CosS3Client(config)
        # file stream simple upload

        with open(file_path, 'rb') as fp:
            logging.info('upload file {} to tencent cos', file_path)
            client.put_object(
                Bucket=self.bucket,
                Body=fp,
                Key='{}/{}}'.format(cos_path, cos_name),
                StorageClass='STANDARD',
                ContentType='text/html; charset=utf-8'
            )
