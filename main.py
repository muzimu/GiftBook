from pathlib import Path
from openai import OpenAI
from os import getenv

client = OpenAI(
    api_key = getenv('api_key'),
    base_url = getenv('base_url'),
)

def recognize():
    file_object = client.files.create(file=Path(r"D:\workspace\python\GiftBook\image\lzj-1.jpg"), purpose="file-extract")
    file_content = client.files.content(file_id=file_object.id).text
    # 把它放进请求中
    messages = [
        {
            "role": "system",
            "content": "你需要整理图片中的信息，并返回一个json对象列表给我，每个json对象包含三个字段：name(姓名), value(金额), remark(备注), 其中金额一般为壹佰元(100)贰佰(200)叁佰(300)",
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
    temperature=0.6,
    )
    
    print(completion.choices[0].message)

def main():
    recognize()


if __name__ == "__main__":
    main()
