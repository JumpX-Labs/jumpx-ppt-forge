# Skill UAT 勾选表 v1（PRD v1.0 闭环）

> **用途**：产品方 / 测试者对 `ai-slide-producer` PRD v1.0 做闭环验收。
> **前提**：`skills/ai-slide-producer/` 已包含 Phase 0–3f 同等内容。
> **不负责**：laogouapi 异步 Jobs、Google nanobanana backend、PPTX 导出、17 套 baoyu preset 全量迁移。

---

## 0. 测试前准备

| # | 项 | 通过 |
|---|-----|:----:|
| 0.1 | 工作目录：`cd skills/ai-slide-producer/` | ☐ |
| 0.2 | Skill 已加载到 Agent（Cursor Skills 指向本目录） | ☐ |
| 0.3 | Agent 模型已选（如 DeepSeek v4）；**出图**走本机脚本 + `.env`，不把 Key 贴进对话 | ☐ |
| 0.4 | 已复制 `.env.example` → `.env`，并填写 OpenAI 兼容网关（示例 laogouapi）： | ☐ |
|     | `IMAGE_BACKEND=openai` | |
|     | `OPENAI_API_KEY=…` | |
|     | `OPENAI_MODEL=gpt-image-2` | |
|     | `OPENAI_BASE_URL=https://<网关>/v1`（须含 `/v1`） | |
| 0.5 | `.env` **未**提交 Git（在 `.gitignore` 内） | ☐ |
| 0.6 | 可选：UAT 项目目录，如 `~/slide-uat/my-deck/`（勿直接改 demo/gallery 源样例） | ☐ |
| 0.7 | 终端执行探测脚本：`python3 scripts/probe_image_backend.py` 输出 JSON 且 `openai.available: true` | ☐ |
| 0.8 | 终端跑连通性检测（可选）：`python3 scripts/probe_image_backend.py --test-connection` 且 `connected: true` | ☐ |
| 0.9 | 确认 Agent 能够在终端执行该 probe，并在 Step 1 Round 1 确认展示中显示 `available` | ☐ |

**网关连通（同步 API，与 Skill 脚本一致）**

```bash
# 在 ai-slide-producer/ 下；勿把 Key 写进本勾选表
set -a && source .env && set +a
curl -sS -o /tmp/uat-img.json -w "HTTP %{http_code}\n" \
  -X POST "${OPENAI_BASE_URL}/images/generations" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-2","prompt":"solid blue gradient, no text","n":1,"size":"1024x1024","quality":"low","output_format":"png"}'
python3 -c "import json; d=json.load(open('/tmp/uat-img.json')); assert d.get('data'), d"
```

| # | 项 | 通过 |
|---|-----|:----:|
| 0.10 | curl 返回 HTTP 200，且 JSON 含 `data[0].b64_json` 或 `url` | ☐ |

---

## A. 脚本回归（固定样例，不依赖 Agent）

在 `skills/ai-slide-producer/` 执行。命令见 [`assets/examples/README.md`](../assets/examples/README.md)。

### A1 — Phase 1 HTML（基线）

```bash
python3 -m py_compile scripts/*.py

python3 scripts/validate_slide_plan.py \
  assets/examples/teaching-clean-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/teaching-clean-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/teaching-clean-demo
python3 scripts/validate_html.py \
  assets/examples/teaching-clean-demo/index.html
```

| # | 项 | 通过 |
|---|-----|:----:|
| A1.1 | 以上命令全部 exit 0 | ☐ |
| A1.2 | 浏览器打开 demo `index.html` 可翻页，无 `{{` 占位符 | ☐ |
| A1.3 | （可选）gallery 10 页同样跑通 | ☐ |

### A2 — Phase 2a Prompt Staging

```bash
python3 scripts/export_images_manifest.py \
  assets/examples/teaching-clean-demo --include-all --backend none
python3 scripts/validate_images_manifest.py \
  assets/examples/teaching-clean-demo
```

| # | 项 | 通过 |
|---|-----|:----:|
| A2.1 | `prompts/` 4 个 `.md`，`source/image_prompts.md` 存在 | ☐ |
| A2.2 | `images_manifest.json` 校验通过；条目 `status: pending`，`default_backend: none` | ☐ |
| A2.3 | **无** `images/slide-*.png`（未调用 API） | ☐ |
| A2.4 | 二次 export 不覆盖已有 prompt 正文（日志含 `kept`） | ☐ |

### A3 — Phase 2b 无 Key / dry-run（禁止假图）

```bash
# 临时去掉 Key 或在新 shell 中不 source .env
python3 scripts/generate_images.py \
  assets/examples/teaching-clean-demo --backend openai --dry-run
python3 scripts/generate_images.py \
  assets/examples/teaching-clean-demo --backend openai
```

| # | 项 | 通过 |
|---|-----|:----:|
| A3.1 | dry-run 打印计划路径，不写 PNG | ☐ |
| A3.2 | 无 Key 时 stderr 有 warning，manifest 仍为 `pending` | ☐ |
| A3.3 | **未**出现空文件或 SVG/HTML 冒充的 PNG | ☐ |

### A4 — Phase 2b 真出图（需 `.env`）

```bash
cd skills/ai-slide-producer   # 确保 load_env 读到 .env
python3 scripts/generate_images.py \
  assets/examples/teaching-clean-demo --backend openai --only P01 --image-size 512px
python3 scripts/validate_images_manifest.py \
  assets/examples/teaching-clean-demo
ls -la assets/examples/teaching-clean-demo/images/slide-01.png
```

| # | 项 | 通过 |
|---|-----|:----:|
| A4.1 | 生成 `images/slide-01.png`（或对应 `output_format` 扩展名） | ☐ |
| A4.2 | manifest 中 P01 `status: ok`，含 `image_file` | ☐ |
| A4.3 | 文件为真实 PNG/JPEG（`file` 命令可辨），非 HTML 改后缀 | ☐ |
| A4.4 | 若曾遇 HTTP 403 / error 1010：确认 `generate_images.py` 已带 `User-Agent`（网关 Cloudflare） | ☐ |

> **注意**：验收后若需保持 demo 仓库「全 pending」回归态，勿提交本地生成的 `images/`；可删 PNG 并将 manifest P01 改回 `pending`。

### A5 — Phase 2c 局部重生

在**副本项目**或 accept demo 被改动的环境：

```bash
cp -R assets/examples/teaching-clean-demo /tmp/asp-uat-regen
python3 scripts/regenerate_slide.py /tmp/asp-uat-regen P03
python3 scripts/build_html.py /tmp/asp-uat-regen
python3 scripts/validate_html.py /tmp/asp-uat-regen/index.html
# 可选出图：
python3 scripts/regenerate_slide.py /tmp/asp-uat-regen P03 --generate --backend openai
```

| # | 项 | 通过 |
|---|-----|:----:|
| A5.1 | 仅 P03 manifest 为 `regenerate-requested`（或文档约定等价态） | ☐ |
| A5.2 | 存在 prompt（及若有图）**backup** 文件 | ☐ |
| A5.3 | 默认重建 `index.html` 且 `validate_html` 通过 | ☐ |
| A5.4 | `--generate` 时仅目标页调 backend，非全 deck 误刷 | ☐ |

### A6 — Phase 3 固定样例（v1.0）

```bash
python3 scripts/build_html.py assets/examples/teaching-clean-layout-gallery
python3 scripts/validate_html.py assets/examples/teaching-clean-layout-gallery/index.html

python3 scripts/build_html.py assets/examples/editorial-magazine-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-demo/index.html

python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-mixed-demo/index.html

python3 scripts/validate_slide_plan.py assets/examples/editorial-magazine-image-first-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py assets/examples/editorial-magazine-image-first-demo/source/style_lock.json
python3 scripts/validate_images_manifest.py assets/examples/editorial-magazine-image-first-demo
python3 scripts/build_html.py assets/examples/editorial-magazine-image-first-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-image-first-demo/index.html

python3 scripts/validate_slide_plan.py assets/examples/swiss-system-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py assets/examples/swiss-system-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/swiss-system-demo
python3 scripts/validate_html.py assets/examples/swiss-system-demo/index.html
```

| # | 项 | 通过 |
|---|-----|:----:|
| A6.1 | teaching-clean gallery、editorial demo、mixed demo 全部 `build_html` + `validate_html` 通过 | ☐ |
| A6.2 | image-first demo 的 `slide_plan`、`style_lock`、`images_manifest`、`index.html` 全部校验通过 | ☐ |
| A6.3 | swiss-system demo 校验通过，可作为第二高视觉档回归样例 | ☐ |
| A6.4 | 7 套 preset 的 CSS / JSON 均存在，且至少有一条 `build_html` + `validate_html` smoke 路径 | ☐ |

---

## B. Agent 对话 UAT（DeepSeek v4 + Skill）

新建空项目目录 `<uat-project>/`，对话中声明：「产物一律写入该路径」。

### B1 — html-only（不耗图额度）

**开场口令示例：**

> 使用 ai-slide-producer，严格按九步与 Gate。输出 **Web / html-only**，风格 teaching-clean，约 **6 页**。目录：`<uat-project>/`。

| # | 项 | 通过 |
|---|-----|:----:|
| B1.1 | Step 1 呈现 Round 1 确认；**Gate 1** 前你回复 `OK` 才继续 | ☐ |
| B1.2 | **Gate 2** 大纲确认后才写 `slide_plan.json` | ☐ |
| B1.3 | **Gate 4** 风格确认后才进入渲染 | ☐ |
| B1.4 | 存在 `source/project_brief.md`、`slide_plan.json`、`style_lock.json` | ☐ |
| B1.5 | 本机 `build_html.py <uat-project>` → `index.html` 可打开（Gate 6） | ☐ |
| B1.6 | 未伪造图片；无 `images/slide-*.png` 冒充完成 | ☐ |

### B2 — image-first（主路径）

**开场口令示例：**

> 输出 **Image / image-first**。我已在 skill 目录配置 OPENAI gpt-image-2（laogouapi）。约 **4 页**。目录：`<uat-project>/`。

| # | 项 | 通过 |
|---|-----|:----:|
| B2.1 | Brief 中 Output Mode 为 `image-first`（Agent 终端成功执行 probe 并在此写入 `probe_json` 明细，Round 1 确认显示 available，非误判 `html-takeover`） | ☐ |
| B2.2 | Gate 4 后存在 `prompts/` + `images_manifest.json`（Agent 或你跑 `export_images_manifest.py`） | ☐ |
| B2.3 | 本机 `generate_images.py <uat-project> --backend openai`（可先 `--only P01`） | ☐ |
| B2.3a | Agent Round 1 或出图前已告知耗时预期（约 **60–90 秒/页**，串行；4 页约 4–6 分钟） | ☐ |
| B2.4 | 至少 1 页 `images/slide-NN.png` + manifest `ok` | ☐ |
| B2.5 | （可选）`build_html.py` + Mixed 页引用图片路径 | ☐ |

### B3 — html-takeover（无 Key 对照）

临时 rename `.env` 或清空 `OPENAI_API_KEY`，新开对话要 Image。

| # | 项 | 通过 |
|---|-----|:----:|
| B3.1 | Round 1 **明示**已切换 HTML，仍保留 Prompts | ☐ |
| B3.2 | 有 `prompts/` + manifest 全 `pending`，**无**假 PNG | ☐ |
| B3.3 | 有可打开 `index.html` | ☐ |

### B4 — 管线铁律抽检

| # | 项 | 通过 |
|---|-----|:----:|
| B4.1 | 未在 Gate 1 前生成整份 `slide_plan` / `index.html` | ☐ |
| B4.2 | 未用 SVG/Canvas/代码绘制冒充 raster | ☐ |
| B4.3 | 改图需求走 `regenerate_slide` 语义，非整包重跑 | ☐ |

---

## C. Phase 3 v1.0 闭环（Agent + 本机）

| # | 项 | 通过 |
|---|-----|:----:|
| C1 | 新主题走通 Gate 1→4，产出 `outline` + `slide_plan` + `style_lock`，无手写 `index.html` | ☐ |
| C2 | `editorial-magazine` demo 浏览器档次明显优于 teaching-clean 工程 demo | ☐ |
| C3 | `editorial-magazine-mixed-demo` 中 P04 / P07 嵌图可见，路径为 `images/slide-*.png` | ☐ |
| C4 | `editorial-magazine-image-first-demo` 含 `prompts/`、manifest、且 ≥4 张 `images/slide-*.png`（占位可） | ☐ |
| C5 | Round 1 或出图前出现 **60–90 秒/页** 的耗时说明 | ☐ |
| C6 | `qa_report.md` 含 Content / Visual / Delivery 三节 | ☐ |

## D. 本机脚本抽检（Peng）

| # | 项 | 通过 |
|---|-----|:----:|
| D1 | `python3 scripts/probe_image_backend.py` 输出 JSON，且 `openai.available: true` | ☐ |
| D2 | 可选真跑：`python3 scripts/generate_images.py <uat-project> --backend openai --only P01`，不提交生成大图 | ☐ |

---

## E. 明确不在 v1.0 UAT 范围

| 项 | 说明 |
|----|------|
| 异步 Jobs | `POST /images/jobs/generations` + GET 轮询；见 `09` 文档，脚本未实现 |
| Google nanobanana | v1.0 后单独立项，不改 `generate_images.py` 新 backend |
| PPTX 导出 | 可选后续 |
| 全 gallery 10 页真出图 | 可选；建议 `--only` 分页测，控制额度 |

---

## F. 验收结论（填一次）

| 字段 | 内容 |
|------|------|
| 测试人 | |
| 日期 | |
| Git 基线 | 如当前 `main` HEAD |
| Agent 模型 | 如 DeepSeek v4 |
| 图片网关 | 如 laogouapi + gpt-image-2 |
| A 脚本回归 | ☐ 通过 / ☐ 未通过 |
| B Agent UAT | ☐ 通过 / ☐ 未通过 / ☐ 跳过 |
| C v1.0 闭环 | ☐ 通过 / ☐ 未通过 / ☐ 跳过 |
| 阻塞问题 | |
| 结论 | ☐ 可进入日常备课试用 / ☐ 需修复后复测 |

---

## 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1 | 2026-05-21 | Phase 2b 后首版；含 laogouapi 同步 API 与 regenerate |
| v1.1 | 2026-05-21 | 扩展 Phase 3 / PRD v1.0 闭环验收：7 preset、Mixed、image-first、视觉档次与耗时预期 |
