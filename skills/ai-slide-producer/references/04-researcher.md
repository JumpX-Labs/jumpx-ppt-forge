# 04 — Researcher

> Step 4 辅助文档。Researcher 在 Writer 写 `slide_plan.json` 前整理证据、素材缺口与事实风险，保证页面计划不是空泛表达。

---

## 角色

> 切换到 **Researcher / Synthesizer**。

职责：

- 从 `context_pack.md` 和 `outline.md` 抽取可用材料。
- 为每页匹配 Key Claims、证据、案例、禁区。
- 标记 `[unverified]` 事实风险。
- 输出 Writer 可直接使用的研究备注，可写入 `source/research_notes.md` 或内嵌到 `slide_plan.json.evidence_refs`。

不做：

- 不编造数据、引用、公司案例。
- 不扩写 on-slide 文案。
- 不替 Designer 选择视觉样式。

---

## 输入

- `source/context_pack.md`
- `source/outline.md`
- 用户补充材料（若有）

---

## 输出：`research_notes.md`（推荐）

```markdown
# Research Notes

**Source Context**: context_pack.md
**Source Outline**: outline.md

## Claim Bank

| Claim ID | Claim | Source | Confidence | Notes |
|----------|-------|--------|------------|-------|
| C01 | <主张> | <用户材料 / brief / inferred> | high / medium / low | <备注> |

## Page Evidence Map

| Page | Needed Evidence | Suggested Claim IDs | Risks |
|------|-----------------|---------------------|-------|
| P01 | <需要什么素材> | C01 | none |
| P03 | <需要什么素材> | C02 | [unverified] |

## Forbidden / Sensitive Points

- <从 context_pack Forbidden Zones 复制>

## Open Gaps

- <需要用户补充或 Writer 避免承诺的空缺>
```

---

## 事实处理规则

- 用户给出的事实可使用，但如果缺来源，标 `Confidence: medium`。
- AI 推断的事实必须标 `Confidence: low` 或 `[unverified]`。
- 数字、排名、法律/医学/金融结论没有来源时，不进入 on-slide text；只能进入 speaker notes 的提醒，或请用户补充。
- 用户禁区优先级高于叙事流畅度。

---

## 给 Writer 的输入约定

Writer 生成每页时：

- `key_message` 必须可追溯到 Claim Bank 或 Outline 的 One-line Purpose。
- `evidence_refs` 使用 `Claim ID`，例如 `["C01", "C03"]`。
- 没有证据的页可保留，但必须是概念、过渡、总结或行动页，不得伪装成事实页。
- `speaker_notes` 可以解释不确定性，`on_slide_text` 不放未经确认的硬事实。

---

## 与其他角色的衔接

| 下一步 | 谁接手 | 用到什么 |
|--------|--------|----------|
| Step 4 Slide Plan | Writer | Claim Bank、Page Evidence Map、Open Gaps |
| Step 5 Review | Reviewer | `evidence_refs` 与 `[unverified]` 标记 |
| Step 8 QA | Reviewer | 复查高风险事实是否仍在可见文本里 |
