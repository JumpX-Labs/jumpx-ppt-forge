# 10 — Style Guard

> Step 8 视觉守门文档。对照 `style_lock.json`、`12-style-presets.md`、最终 HTML / Image 产物检查风格一致性与可见结果质量。

---

## 角色

> 切换到 **Style Guard**。

职责：

- 检查颜色、字体、密度、layout、图片契约是否遵守 Style Lock。
- 识别视觉漂移、占位符残留、图片缺失、文本溢出风险。
- 给 Step 8 的 `qa_report.md` 写 **Visual (Style Guard)** 小节。

不做：

- 不审核事实与叙事逻辑；那是 Reviewer。
- 不整理最终目录和 README；那是 Producer。
- 不发明 `style_lock.json` 之外的配色/字体（守的就是 style_lock）。

---

## 输入

- `source/style_lock.json`
- `source/slide_plan.json`
- `index.html`（若有）
- `images/`（若有）
- `images_manifest.json`（若有）
- `assets/styles/<style_name>.css`
- `assets/style-presets/<style_name>.json`
- [`12-style-presets.md`](12-style-presets.md)

缺少 `style_lock.json` 或 `slide_plan.json` 时，停止并回到对应上游步骤。

---

## 与 Reviewer / Producer 的边界

| 角色 | 检查范围 | 输出 |
|------|----------|------|
| Reviewer | 内容、事实、叙事、受众匹配 | `review_report.md` 与 `qa_report.md` 的 Content 小节 |
| Style Guard | 颜色、字体、密度、layout 漂移、图片缺失、占位符、溢出风险 | `qa_report.md` 的 Visual 小节 |
| Producer | 目录结构、README、可见产物、Gate 6 | `qa_report.md` 的 Delivery 小节与项目 `README.md` |

---

## 检查表

| 检查项 | 标准 | 结果 |
|--------|------|------|
| CSS 变量 | `index.html` 内 `:root` 的 `--asp-bg` / `--asp-ink` / `--asp-accent` / fonts 来自 `style_lock.json` | pass / warn / fail |
| Preset 漂移 | 最终观感符合 `style_name`；例如 `editorial-magazine` 不应退回灰卡片模板站感，`swiss-system` 不应出现渐变和多 accent | pass / warn / fail |
| 占位符 | 最终 HTML 无 `{{...}}` | pass / fail |
| 图片契约 | Mixed 下 `needed=true` 页有 `images/slide-NN.*` 或 manifest 状态说明；缺图显示 `Image pending (slide-NN)` | pass / warn / fail |
| 文本密度 | 对照 `style_lock.density` 与 `14-quality-checklist.md` 密度表；body 超限 warning | pass / warn |
| Layout 完整 | section 数 = `deck_meta.total_pages`；`data-layout` 与 `slide_plan.pages[].layout_type` 一致 | pass / fail |
| 溢出风险 | 标题过长、body > 6、comparison > 4、timeline/framework/closing > 6 均 warning | pass / warn |
| 可见图片 | `image-text` 页的 `<img>` 在浏览器中可见，不是断裂图 | pass / warn / fail |

---

## 返工决策

| 问题 | 处理 |
|------|------|
| 颜色 / 字体与 Style Lock 不一致 | 指出偏差，让 Web Renderer 按 `style_lock.json` 重写相关页 |
| Preset 漂移严重 | 回到 Gate 4 让用户重审风格，或切换 preset 后重跑 Step 6–7 |
| 某页版式/可读性差（溢出、层级乱） | 让 Web Renderer 按 08 硬契约重写该页 |
| Mixed 有图页文件缺失 | 若 backend 可用，跑 `generate_images.py` 或 `regenerate_slide.py <project> PNN --generate`；否则在 QA 中标 warning |
| 图片生成失败但 HTML 可读 | `qa_report.md` 标 warning，不阻塞 html-takeover / html-only-with-prompts |
| 图片生成失败且用户只要 Image | Gate 5 fail，必须重试、换 backend 或改为 HTML takeover |
| 单页视觉问题 | 优先局部重生：`regenerate_slide.py <project> PNN`；不要整包重跑 |

---

## `qa_report.md` Visual 小节模板

```markdown
## Visual (Style Guard)

| Check | Status | Notes |
|-------|--------|-------|
| Style lock variables | pass | Colors and fonts match `style_lock.json`. |
| Preset fit | pass | Output reads as `<style_name>`. |
| Placeholders | pass | No `{{...}}` remains. |
| Image contract | pass | Mixed image pages have local `images/slide-NN.*`. |
| Density / overflow | pass-with-warnings | <notes or none> |

### Visual Decision

pass | pass-with-warnings | fail
```

---

## 最低可执行检查

无新增脚本时，Style Guard 至少执行：

```bash
python3 scripts/validate_html.py <project>/index.html
python3 scripts/validate_slide_plan.py <project>/source/slide_plan.json
python3 scripts/validate_context_lock.py <project>/source/style_lock.json
```

然后人工打开浏览器检查 `cover`、`image-text`、`comparison`、`closing` 等关键页。
