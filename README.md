# TikTok 本地化文案生成服务

这个项目实现了你要的能力：
1. 上传视频。
2. 自动读取视频内容（调用 OpenAI 转写模型）。
3. 按所选国家生成可发布到该国家 TikTok 的文案方案。

## 如何使用

### 1) 安装依赖

```bash
pip install -r requirements.txt
```

### 2) 配置模式（二选一）

#### 真实模式（推荐）

```bash
export OPENAI_API_KEY=your_key_here
```

#### 演示模式（无 Key 也可跑通）

```bash
export USE_MOCK_AI=true
```

> 演示模式会返回 mock 转写与 mock 文案，方便先联调接口。

### 3) 启动服务

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4) 健康检查

```bash
curl http://127.0.0.1:8000/health
```

返回：

```json
{"status":"ok"}
```

### 5A) 上传视频直接生成（完整流程）

```bash
curl -X POST "http://127.0.0.1:8000/generate" \
  -F "country=Indonesia" \
  -F "brand_context=主打轻量透气，适合夏季通勤" \
  -F "video=@/path/to/demo.mp4"
```

### 5B) 先传转写文本再生成（最快联调）

```bash
curl -X POST "http://127.0.0.1:8000/generate-from-transcript" \
  -H "Content-Type: application/json" \
  -d '{
    "country": "Indonesia",
    "transcript": "视频展示了一款防晒喷雾，包含上脸前后对比和通勤场景。",
    "brand_context": "敏感肌可用，轻薄不搓泥"
  }'
```

## API 说明

### `POST /generate`

- `country` (form): 目标国家，如 `Indonesia` / `Brazil` / `US`
- `brand_context` (form, optional): 品牌或商品补充信息
- `video` (file): 视频文件

限制：
- 只支持常见视频后缀：`.mp4 .mov .m4v .avi .webm .mpeg .mpg`
- 文件大小不超过 50MB

### `POST /generate-from-transcript`

- `country` (json): 目标国家
- `transcript` (json): 已有的视频内容转写文本
- `brand_context` (json, optional): 品牌/商品补充信息

返回示例：

```json
{
  "transcript": "...视频转写文本...",
  "generated": {
    "market_language": "id",
    "hooks": ["...", "...", "..."],
    "caption_options": ["...", "...", "..."],
    "hashtag_sets": [["#..."], ["#..."], ["#..."]],
    "cta_options": ["...", "...", "..."],
    "compliance_notes": "..."
  }
}
```

## 设计说明

- `src/service.py`
  - `transcribe_video`: 真实模式使用 `gpt-4o-mini-transcribe`；演示模式返回 mock 转写。
  - `generate_copy`: 真实模式调用 `gpt-4o-mini` 并校验返回结构；演示模式返回 mock 文案。
- `src/prompts.py`
  - 统一封装本地化营销提示词，确保输出结构稳定。
- `src/schemas.py`
  - 定义结构化输入/输出模型，约束字段完整性。

## 测试

```bash
pytest -q
```
