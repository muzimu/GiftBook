import boto3
from os import getenv
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client('s3',
                  region_name='cn-east-1', # 华东-浙江区 region id
                  endpoint_url=getenv("s3_url"), # 华东-浙江区 endpoint
                  aws_access_key_id=getenv("s3_ak"),
                  aws_secret_access_key=getenv("s3_sk"),
                  config=boto3.session.Config(signature_version="s3v4"))


def upload_file(file_path: str):
    file_name = file_path.split("/")[-1]
    with open(file_path, 'rb') as f:
        s3.put_object(Bucket='muzimu', Key='GiftBook/' + file_name, Body=f, IfNoneMatch='*')
        
# upload_file('image/lzj-1.jpg')