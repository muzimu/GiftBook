# How To Deploy

 - 创建文件夹image, 将需要识别的图片放在里面
 - 项目根目录下创建.env文件，内容示例如下

```
api_key = "API-KEY"
base_url = "https://api.moonshot.cn/v1"
```

```
base_url = "https://openai.qiniu.com/v1"
api_key = "API-KEY"
# 可参考 https://muzimu.github.io/ 中博客文章
model = "moonshotai/kimi-k2-0905"
```

# How to build uv environment

> uv官方安装教程 https://docs.astral.sh/uv/getting-started/installation/

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
uv run main.py
```
