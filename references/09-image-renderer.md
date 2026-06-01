# 09 — Image Renderer

> Step 7A 落地文档。分两阶段：**先导出可编辑的 Prompt 文件，再按需调用出图 API**。

---

## 角色

> 切换到 **Image Renderer**。

职责：

- **准备 Prompt（7A-P）**：从 `slide_plan.json` + `style_lock.json` 生成 `prompts/` 与 `images_manifest.json`。
- **调用出图（7A-G）**：读取 Prompt 与 manifest，调用真实图片 backend（禁止伪造位图）。
- 禁止用 HTML / SVG / Canvas / 代码绘制伪造 raster image。

---

## 第一步：导出 Prompt（7A-P）

由脚本机械导出，不调用出图 API：

```text
source/slide_plan.json
source/style_lock.json
assets/templates/image-prompt-template.md
        ↓ scripts/export_images_manifest.py
prompts/NN-slide-{slug}.md
images_manifest.json
source/image_prompts.md
```

Agent 或人工可以在 Gate 4 后编辑 `prompts/*.md` 正文，再进入 `generate_images.py`。

默认不覆盖已有 Prompt；传 `--force` 才备份并重写。

---

## 页面选择规则

| Output Mode | 默认导出 Prompt |
|-------------|----------------|
| `image-first` | 全部页面 |
| `mixed` | `image_requirement.needed == true` 的页面 |
| `html-takeover` | `image_requirement.needed == true` 的页面 |
| `html-only-with-prompts` | `image_requirement.needed == true` 的页面 |
| `html-only` | 不导出，除非传 `--include-all` |

`--include-all` 用于回归、Prompt 审核或用户明确要全量资产化。

---

## Prompt Staging 规则

- 每页生成前必须重读 `source/style_lock.json`。
- Prompt frontmatter 字段必须对齐 `schemas/image_prompts.schema.json`。
- `style_lock_ref` 固定写 `source/style_lock.json`。
- `generated_image_path` 写目标路径 `images/slide-NN.png`，即使图片还没生成。
- 无 backend 时 `image_backend: "none"`，manifest entry `status: "pending"`。
- 不调用任何图片 API。
- 不生成占位 PNG。

---

## Manifest 状态

此步 manifest 只产生：

| 状态 | 含义 |
|------|------|
| `pending` | Prompt 已落盘，尚未调用 backend |

出图步骤会使用：

| 状态 | 含义 |
|------|------|
| `generating` | 正在生成 |
| `ok` | 图片文件存在 |
| `failed` | backend 返回失败，可重试 |
| `needs-manual` | 自动生成放弃，但不阻断 HTML 交付 |
| `regenerate-requested` | 被局部重生流程标记 |

---

## 运行方式

```bash
python3 scripts/export_images_manifest.py <project-dir>
python3 scripts/export_images_manifest.py <project-dir> --include-all
python3 scripts/export_images_manifest.py <project-dir> --force
```

**7A-P 验收**（须全部满足）：

- 产生 `prompts/` 和 `images_manifest.json`。
- 产生 `source/image_prompts.md`。
- 不产生 `images/slide-*.png`。
- 已有 Prompt 在无 `--force` 时不被覆盖。

**7A-G 运行**：

```bash
python3 scripts/generate_images.py <project-dir> --backend openai
python3 scripts/generate_images.py <project-dir> --backend nanobanana
python3 scripts/generate_images.py <project-dir> --backend gemini
python3 scripts/probe_image_backend.py <project-dir> --test-connection
python3 scripts/generate_images.py <project-dir> --only P01
python3 scripts/generate_images.py <project-dir> --dry-run
```

7A-G 规则：

- 只处理 `pending` / `failed` / `needs-manual` / `regenerate-requested`，`ok` 默认跳过。
- `--force` 才重生已存在图片或 `ok` 条目。
- `--only` 可传 slide id、页序号或 prompt 文件名，逗号分隔。
- 无对应 API Key 时保持 `pending`，只输出 warning（OpenAI / Nano Banana / Gemini 见下）。
- backend 返回错误时标记 `needs-manual`，写 `error_message`，继续处理后续页。
- 成功后写入 `images/slide-NN.*`，并回写 `image_file`、`status: ok`、`updated_at`。

---

## 生成耗时预期（必须告知用户）

本 Skill 的 `generate_images.py` **按页串行**调用同步 API（`POST …/images/generations`），每页一次 HTTP 往返，**不会**在 Agent 对话里“秒出全 deck”。

| 参考值 | 说明 |
|--------|------|
| **单页（OpenAI 网关）** | 约 **60–90 秒**（本机 laogouapi + `gpt-image-2` 实测约 **62s/页**） |
| **单页（Nano Banana / Google）** | 通常 **数秒–30 秒** 量级（视模型与配额；需本机实测后写入 Round 1 预期） |
| **4 页全出图** | 约 **4–6 分钟** |
| **10 页全出图** | 约 **10–15 分钟** |
| **Mixed（2–3 张图）** | 约 **2–5 分钟**（其余页走 HTML，较快） |

**Agent / Producer 必须在调用 `generate_images.py` 之前**向用户说明：

1. 页数 × 单页耗时的大致等待时间；
2. 脚本在终端运行，期间可继续改 `prompts/` 或先做 HTML（Mixed 时图片完成后再 `build_html`）；
3. 冒烟可用 `--only P01`；不必一次生成全部页。

**不建议**在未设预期时一次性对 20+ 页执行全量出图；页数多时应建议减少 `image_requirement.needed`、改用 `mixed` / `html-only`，或分批 `--only`。

Backend 配置来自当前环境或 `.env`，当前环境优先。OpenAI 使用：

```env
IMAGE_BACKEND=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-image-2
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_OUTPUT_FORMAT=png
```

Gemini 使用（与 Nano Banana 同一 API，legacy backend id）：

```env
IMAGE_BACKEND=gemini
GEMINI_API_KEY=xxx
GEMINI_MODEL=gemini-3.1-flash-image-preview
GEMINI_BASE_URL=https://generativelanguage.googleapis.com
```

### Google Nano Banana（推荐 backend id：`nanobanana`）

Nano Banana 是 Google **Gemini Image** 的产品名，走 **Gemini API** 的 `generateContent`，不是 OpenAI `/images/generations`。

| 产品名 | 模型 ID（`NANOBANANA_MODEL`） |
|--------|------------------------------|
| Nano Banana 2（默认） | `gemini-3.1-flash-image-preview` |
| Nano Banana Pro | `gemini-3-pro-image-preview` |
| Nano Banana（上一代） | `gemini-2.5-flash-image` |

也可用别名：`nano-banana-2` / `nano-banana-pro` / `nano-banana`（脚本会映射到上表）。

**HTTP 调用（与 `generate_images.py` 一致）**：

```http
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}
Content-Type: application/json

{
  "contents": [{ "role": "user", "parts": [{ "text": "<prompt>" }] }],
  "generationConfig": {
    "responseModalities": ["IMAGE"],
    "imageConfig": { "aspectRatio": "16:9", "imageSize": "1K" }
  }
}
```

响应从 `candidates[].content.parts[].inlineData.data` 取 base64 PNG。

**环境变量**（二选一 Key；推荐独立命名）：

```env
IMAGE_BACKEND=nanobanana
NANOBANANA_API_KEY=your-google-ai-studio-key
NANOBANANA_MODEL=gemini-3.1-flash-image-preview
NANOBANANA_BASE_URL=https://generativelanguage.googleapis.com
```

`NANOBANANA_API_KEY` 未设置时，可回退使用 `GEMINI_API_KEY`（同一 Google key）。

Key 获取：[Google AI Studio API keys](https://aistudio.google.com/apikey)

维护者排错与 API 细节见 `docs/plan-nanobanana-backend_v1.md`（Agent 日常不必读）。

---

## OpenAI 兼容网关：同步 vs 异步 Jobs

`scripts/generate_images.py` **当前仅实现同步路径**：

```http
POST {OPENAI_BASE_URL}/images/generations
```

部分 OpenAI 兼容网关同时提供 **异步 Jobs**，适合长耗时、批量或避免 HTTP 超时。当前 `generate_images.py` **未内置** Jobs 轮询；需时可手工 curl，或后续为脚本增加 `--async-jobs`。

| 步骤 | 方法 | 路径（相对 `OPENAI_BASE_URL`） |
|------|------|--------------------------------|
| 提交生成 | `POST` | `/images/jobs/generations` |
| 提交编辑 | `POST` | `/images/jobs/edits` |
| 轮询结果 | `GET` | `/images/jobs/{job_id}` |

`OPENAI_BASE_URL` 须带 `/v1` 前缀，例如 `https://laogouapi.com/v1`，则完整 URL 为 `https://laogouapi.com/v1/images/jobs/generations`。

### 异步示例（生成）

```bash
# 1) 提交任务（body 字段与同步 generations 类似：model、prompt、size、quality 等）
curl -X POST "${OPENAI_BASE_URL}/images/jobs/generations" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "a tiny orange cat astronaut",
    "n": 1
  }'
# 响应中取出 job_id（字段名以网关文档为准，常见为 id / job_id）

# 2) 轮询直到 completed / failed
curl "${OPENAI_BASE_URL}/images/jobs/{job_id}" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}"
# 从终态响应取 b64_json 或 url，再写入 images/slide-NN.png
```

编辑任务：对已有图做 inpaint / 改图时用 `POST /images/jobs/edits`（参数以网关文档为准），同样用 `GET /images/jobs/{job_id}` 取结果。

### 与 Skill 的关系

| 方式 | 状态 | 适用 |
|------|------|------|
| 同步 `POST /images/generations` | ✅ `generate_images.py` 已用 | 单页冒烟、demo 回归（已验证 laogouapi） |
| 异步 Jobs + 轮询 | 📋 文档记录；脚本未实现 | 大批量 deck、网关要求异步时 |

manifest 状态机不变：异步完成后仍应回写 `status: ok` 与 `image_file`，禁止在未拿到 raster 前标记成功。
