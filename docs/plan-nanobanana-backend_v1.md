# Google Nano Banana 生图接入说明 v1

| 字段 | 值 |
|------|-----|
| 状态 | **已接入**（`--backend nanobanana`） |
| 实现 | `scripts/generate_images.py` + `scripts/probe_image_backend.py` |
| 关联 | [`references/09-image-renderer.md`](../references/09-image-renderer.md) |

---

## 1. 它是什么

**Nano Banana** = Google **Gemini Image** 系列的产品名，开发者通过 **Gemini API**（Google AI Studio / AI Studio API key）出图。

本 Skill **不**单独接一套未知 HTTP；而是：

- 新增 backend id：**`nanobanana`**
- 底层调用与 `gemini` 相同：`POST …/v1beta/models/{model}:generateContent`，`responseModalities: ["IMAGE"]`

---

## 2. 模型对照

| 产品名 | 模型 ID |
|--------|---------|
| Nano Banana 2（默认） | `gemini-3.1-flash-image-preview` |
| Nano Banana Pro | `gemini-3-pro-image-preview` |
| Nano Banana | `gemini-2.5-flash-image` |

环境变量别名（可选）：`nano-banana-2` / `nano-banana-pro` / `nano-banana`。

---

## 3. 你怎么配置（Peng 已备好 Key 时）

在 `skills/ai-slide-producer/.env` 增加（**不要提交 Git**）：

```env
IMAGE_BACKEND=nanobanana
NANOBANANA_API_KEY=<你的 Google AI Studio API Key>
NANOBANANA_MODEL=gemini-3.1-flash-image-preview
```

也可继续用 `GEMINI_API_KEY` + `IMAGE_BACKEND=gemini`（行为等价，manifest 里 backend 显示为 `gemini`）。

---

## 4. 探测与出图命令

```bash
cd skills/ai-slide-producer

python3 scripts/probe_image_backend.py assets/examples/teaching-clean-demo --test-connection

python3 scripts/export_images_manifest.py assets/examples/teaching-clean-demo --include-all --backend nanobanana

python3 scripts/generate_images.py assets/examples/teaching-clean-demo --backend nanobanana --only P01

# 强制重生成
python3 scripts/generate_images.py assets/examples/teaching-clean-demo --backend nanobanana --only P01 --force
```

`probe` 成功时 JSON 含：

```json
"nanobanana": { "available": true, "model": "gemini-3.1-flash-image-preview", "connected": true }
```

---

## 5. 与 OpenAI（laogouapi）并存

| | OpenAI 网关 | Nano Banana |
|--|-------------|-------------|
| backend id | `openai` | `nanobanana` |
| 端点 | `{OPENAI_BASE_URL}/images/generations` | `generativelanguage.googleapis.com/.../generateContent` |
| 本机实测耗时 | ~62s/页（gpt-image-2） | 待你填 Key 后实测 |
| 切换 | `IMAGE_BACKEND=openai` | `IMAGE_BACKEND=nanobanana` |

同一项目 manifest 的 `backend` 字段应与当次生成一致；换 backend 建议 `export … --force` 后重跑 `generate_images`。

---

## 6. Agent 侧注意

- CraftAgents **看不到** `.env` 时，Step 1 须跑 `probe_image_backend.py` 并把 `nanobanana` 可用性写入 `project_brief.md`。
- Round 1 须写清：Nano Banana 走本机脚本、非对话瞬时出图；耗时见 `09` §生成耗时预期。

---

## 7. 官方文档

- [Gemini API 图片生成](https://ai.google.dev/gemini-api/docs/image-generation)
- [API Key](https://aistudio.google.com/apikey)
- [Nano Banana 2 开发者博文](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-nano-banana-2)
