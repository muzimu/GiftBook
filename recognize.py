import csv
import s3
import json
from pathlib import Path
from typing import List
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()

client = OpenAI(
    api_key = getenv('api_key'),
    base_url = getenv('base_url'),
)

# 定义数据类作为结构体
@dataclass
class Gift:
    name: str       # 姓名
    value: int      # 金额
    remark: str     # 备注
    img: str        # 图片链接

def recognize(file_path: str, img: str) -> List[Gift]:
    file_object = client.files.create(file=Path(file_path), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text
    # 把它放进请求中
    messages = [
        {
            "role": "system",
            "content": "你需要整理图片中的信息，并返回一个json对象列表给我，每个json对象包含三个字段：name(姓名), value(金额), remark(备注), 其中金额一般为下面几种金额：60(陆拾元),100(壹佰元),200(贰佰元),300(叁佰元),400(肆佰元)。有的合计金额需要拆分成多个人的礼金，请分别列出每个人的礼金信息并在备注中标注。请严格按照要求的格式返回，不要有任何多余的内容，返回的json对象列表必须是一个合法的json数组，不能有多余的逗号等符号。图片中有12个人的贺礼信息，必须要有12个json对象，且识别顺序为从左至右，如果贺礼确实为空，金额填0。如果没有合礼或者在括号中添加备注的情况，默认情况备注字段统一使用‘贺礼’。",
        },
        {
            "role": "user",
            "content": file_content
        },
        {
            "role": "assistant",
            "content": "[",
            "partial": True
        }
    ]
    
    # 然后调用 chat-completion, 获取 Kimi 的回答
    completion = client.chat.completions.create(
        model=getenv('model'),
        messages=messages,
    )
    json_str = '[' + completion.choices[0].message.content.replace('\n', '').replace('}{', '},{')
    
    # 解析JSON字符串为字典列表
    data = json.loads(json_str)
    
    # 转换为Gift对象列表
    return [Gift(**item, img=img) for item in data]