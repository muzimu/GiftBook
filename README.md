# How To Deploy

 - 创建文件夹image, 将需要识别的图片放在里面
 - 项目根目录下创建.env文件，内容示例如下

```
api_key = "API-KEY"
base_url = "https://api.moonshot.cn/v1"
```

# How to build uv environment

```bash
pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
pip install uv -i https://mirrors.aliyun.com/pypi/simple
uv sync
uv run main.py
```