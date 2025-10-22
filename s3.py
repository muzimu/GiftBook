import boto3
from os import getenv
from dotenv import load_dotenv
import requests
load_dotenv()
s3 = boto3.client('s3',
                  region_name='cn-east-1', # 华东-浙江区 region id
                  endpoint_url=getenv("s3_url"), # 华东-浙江区 endpoint
                  aws_access_key_id=getenv("s3_ak"),
                  aws_secret_access_key=getenv("s3_sk"),
                  config=boto3.session.Config(signature_version="s3v4"))

def check_url_accessibility(url, timeout=5):
    """检查图片URL是否可访问，结果缓存10分钟"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code in [200, 302]
    except (requests.exceptions.RequestException, Exception):
        return False

def upload_file(file_path: str):
    try:
        file_name = file_path.split("/")[-1]
        img_url = f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{file_name}"
        if not check_url_accessibility(img_url):
            with open(file_path, 'rb') as f:
                s3.put_object(Bucket='muzimu', Key='GiftBook/' + file_name, Body=f, IfNoneMatch='*')
        return img_url
        
    except Exception as e:
        print(f"文件上传失败: {str(e)}")
        return e
        
# upload_file('image/lzj-1.jpg')