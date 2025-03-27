# fee

下载依赖

```bash
cd fee
uv sync
```

设置环境变量,在`.env`文件里写好 pg 数据库的配置

```bash
cp .env.example .env
```

运行

```bash
uv run fastapi dev ./main.py
```
