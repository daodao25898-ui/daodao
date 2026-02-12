# TikTok 本地化文案生成服务

这个项目实现了你要的能力：
1. 上传视频。
2. 自动读取视频内容（调用 OpenAI 转写模型）。
3. 按所选国家生成可发布到该国家 TikTok 的文案方案。

## 启动

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## API

### `POST /generate`

- `country` (form): 目标国家，如 `Indonesia` / `Brazil` / `US`
- `brand_context` (form, optional): 品牌或商品补充信息
- `video` (file): 视频文件

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
  - `transcribe_video`: 使用 `gpt-4o-mini-transcribe` 提取视频文本。
  - `generate_copy`: 使用 `gpt-4o-mini` 生成国家本地化 TikTok 文案（JSON）。
- `src/prompts.py`
  - 统一封装了本地化营销提示词，确保输出结构稳定。

## 测试

```bash
pytest -q
```
