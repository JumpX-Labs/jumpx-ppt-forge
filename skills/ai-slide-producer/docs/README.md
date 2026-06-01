# Docs（维护者与 QA）

> **Agent 日常不必读本目录。** 跑课、做 deck 请以 [`SKILL.md`](../SKILL.md) 与 [`references/`](../references/) 为准。

本目录存放实施记录、UAT 勾选表、backend 排错说明。文件名里的 `phase*` 是内部开发批次编号，与使用者无关。

| 文档 | 说明 |
|------|------|
| [`skill-uat-checklist_v1.md`](skill-uat-checklist_v1.md) | v1.0 闭环验收勾选（脚本 + Agent + 固定样例） |
| [`plan-agent-backend-probe_v1.md`](plan-agent-backend-probe_v1.md) | CraftAgents / `.env` 探测排错（已实施） |
| [`plan-nanobanana-backend_v1.md`](plan-nanobanana-backend_v1.md) | Google Gemini Image（`--backend nanobanana`） |
| [`phase2-implementation-brief_v1.md`](phase2-implementation-brief_v1.md) | 出图与 Prompt 导出实施记录 |
| [`phase3-implementation-brief_v1.md`](phase3-implementation-brief_v1.md) | v1 收口总览 |
| [`phase3c-3d-executor-brief_v1.md`](phase3c-3d-executor-brief_v1.md) | Mixed 样例 + Style Guard / Producer |
| [`phase3e-3f-executor-brief_v1.md`](phase3e-3f-executor-brief_v1.md) | 7 preset + image-first 样例 + UAT |
| [`teaching-clean-layout-gallery-prd_v1.md`](teaching-clean-layout-gallery-prd_v1.md) | Layout Gallery 10 页回归任务书 |

上级 monorepo 另有产品 PRD / 实施总纲（`jumpx-ppt-slides-skill/` 根），不在本 Git 仓库内。
