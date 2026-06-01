# 06 — Reviewer

> Step 5 落地文档。自动审核 `slide_plan.json`，最多自动返工一轮。

---

## 角色

> 切换到 **Narrative Reviewer**。

职责：

- 检查叙事、事实风险、重复遗漏、受众匹配。
- 只审内容与结构，不审视觉风格。
- 输出 `source/review_report.md`。

---

## 输入

- `source/context_pack.md`
- `source/outline.md`
- `source/slide_plan.json`

若任一文件缺失，停止并回到对应上游步骤。

---

## 审核清单

| 检查项 | 通过标准 | 严重度 |
|--------|----------|--------|
| 主线 | 每页能连成一条清楚叙事线 | critical |
| 页面功能 | 每页承担不同作用，不只是换标题复述 | critical |
| 衔接 | 相邻页面有承接关系 | warning |
| 受众 | 概念深度匹配 Audience | critical |
| 事实 | 数字、引用、案例有来源或标为 `[unverified]` | critical |
| 密度 | 每页文本量符合 `style_lock.density` 预期 | warning |
| 重复 | 同一观点不连续重复出现 | warning |
| 遗漏 | Context Pack 的关键约束和 must include 被覆盖 | critical |

---

## 返工策略

与 `SKILL.md` Step 5 对齐：

| 结果 | 下一步 |
|------|--------|
| 无 issue | 进入 Step 6 |
| 仅 warning | 记录 warning，进入 Step 6 |
| 1 处 critical | Writer 自动增量改相关页，再复审一次 |
| 2+ critical | 回退 Gate 2，让用户重审 Outline |
| 自动改后仍 critical | 回退 Gate 2，禁止继续自动重写 |

---

## `review_report.md` 模板

```markdown
# Review Report

**Status**: pass | pass-with-warnings | rework-required
**Reviewer**: Narrative Reviewer
**Source Plan**: slide_plan.json

## Summary
<3 行内总结>

## Issues

| Severity | Page | Finding | Required Action |
|----------|------|---------|-----------------|
| warning | P03 | <问题> | <建议> |

## Coverage

- Main arc: pass | warning | fail
- Audience fit: pass | warning | fail
- Must include: pass | warning | fail
- Forbidden zones: pass | warning | fail
- Unverified claims: none | listed below

## Decision

<pass / pass-with-warnings / return-to-writer / return-to-outline>
```

---

## 与其他角色的衔接

| 下一步 | 条件 |
|--------|------|
| Designer | `Status` 为 `pass` 或 `pass-with-warnings` |
| Writer | 仅 1 处 critical，可自动改一轮 |
| Strategist / 用户 | 2+ critical 或自动改后仍失败 |

