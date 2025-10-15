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
            "content": "你需要整理图片中的信息，并返回一个json对象列表给我，每个json对象包含三个字段：name(姓名), value(金额), remark(备注), 其中金额一般为下面几种金额：60(陆拾元),100(壹佰元),200(贰佰元),300(叁佰元),400(肆佰元)。有的合计金额需要拆分成多个人的礼金，请分别列出每个人的礼金信息并标注。请严格按照要求的格式返回，不要有任何多余的内容，返回的json对象列表必须是一个合法的json数组，不能有多余的逗号等符号。图片中有12个人的贺礼信息，必须要有12个json对象。",
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
        model="kimi-k2-0905-preview",
        messages=messages,
    )
    json_str = '[' + completion.choices[0].message.content.replace('\n', '').replace('}{', '},{')
    
    # 解析JSON字符串为字典列表
    data = json.loads(json_str)
    
    # 转换为Gift对象列表
    return [Gift(**item, img=img) for item in data]

def append_gifts_to_csv(gifts: List[Gift], csv_file: str):
    """将Gift对象列表追加写入CSV文件"""
    
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        # 定义CSV字段名，与现有文件保持一致
        fieldnames = [
            '时间', '分类', '二级分类', '类型', '金额', 
            '账户1', '账户2', '备注', '账单标记', 
            '手续费', '优惠券', '标签', '账单图片'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # 遍历Gift对象并写入CSV
        for gift in gifts:
            # 构建一行数据，映射Gift对象属性到CSV字段
            row = {
                '时间': "2021/6/18",
                '分类': '礼金',
                '二级分类': '',
                '类型': '收入',
                '金额': gift.value,
                '账户1': '',
                '账户2': '',
                '备注': f'{gift.name} {gift.remark} {gift.img}',
                '账单标记': '',
                '手续费': '',
                '优惠券': '',
                '标签': '',
                '账单图片': f'"{gift.img}"'
            }
            writer.writerow(row)

def process(file_path:str):
    # s3.upload_file(file_path)
    gifts = recognize(file_path, f"http://t44p80tuo.hd-bkt.clouddn.com/GiftBook/{file_path.split('/')[-1]}")
    append_gifts_to_csv(gifts, 'output/template.csv')

def main():
    process("image/lzj-1.jpg")

if __name__ == "__main__":
    main()
