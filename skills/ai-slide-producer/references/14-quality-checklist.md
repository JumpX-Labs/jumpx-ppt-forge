# 14 — Quality Checklist

> Step 8 总检查表。内容复检见 `06-reviewer.md`，视觉守门详见 `10-style-guard.md`，交付组装详见 `11-producer.md`。

---

## 角色

> 切换到 **Quality Checker**（Reviewer + Style Guard + Producer）。

职责：

- 汇总内容、视觉、交付三类检查。
- 输出 `<project>/qa_report.md`。
- Gate 5 失败时要求局部返工。

---

## HTML 检查

| 项 | 通过标准 |
|----|----------|
| 文件存在 | `<project>/index.html` 存在且非空 |
| 页数 | section 数 = `slide_plan.deck_meta.total_pages` |
| 占位符 | 无残留 `{{...}}` |
| 交互 | HTML 包含 Prev/Next、键盘、触摸、ESC 索引逻辑 |
| 本地打开 | 不依赖构建工具；CSS 和 JS 内联 |
| 样式锁 | CSS 变量来自 `style_lock.json` |
| 文本 | 没有未转义的明显脚本片段 |

---

## 内容检查

- `review_report.md` 不含 unresolved critical。
- 每页 `key_message` 非空。
- `on_slide_text.body` 不超过密度建议：
  - `low`: 2 条以内
  - `medium-low`: 3 条以内
  - `medium`: 4 条以内
  - `medium-high`: 5 条以内
  - `high`: 6 条以内

---

## 交付检查

- 目录结构符合 `15-export-contract.md`。
- `source/slide_plan.json` 通过 schema 与 semantic validation。
- `source/style_lock.json` 通过 schema。
- `README.md` 写明怎么看、怎么改、怎么续生。

---

## `qa_report.md` 模板

```markdown
# QA Report

**Status**: pass | pass-with-warnings | fail
**Output Mode**: <from context_pack>
**Checked**: YYYY-MM-DD

## Summary
- <结果 1>
- <结果 2>
- <结果 3>

## Content (Reviewer)

| Check | Status | Notes |
|-------|--------|-------|
| Main arc | pass | <notes> |
| Audience fit | pass | <notes> |
| Critical issues | pass | none |

## Visual (Style Guard)

| Check | Status | Notes |
|-------|--------|-------|
| Style lock variables | pass | <notes> |
| Preset fit | pass | <notes> |
| Placeholders | pass | none |
| Image contract | pass | <notes> |
| Density / overflow | pass | <notes> |

## Delivery (Producer)

| Check | Status | Notes |
|-------|--------|-------|
| Result visible | pass | <HTML or images> |
| Export tree | pass | <notes> |
| README | pass | <notes> |
| Manifest | pass | <notes or n/a> |

## Follow-ups

- <warning / backlog / none>
```
