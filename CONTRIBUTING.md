# 贡献指南 · Contributing

谢谢你愿意改进 **AI PPT Forge**！这是一个**可装进任意 Agent 的 Skill**——核心是提示词、契约与确定性校验脚本，不是一个传统应用。下面是怎么参与。

## 仓库怎么组织

| 路径 | 是什么 | 改它影响 |
|---|---|---|
| `SKILL.md` | Agent 入口：触发、九步管线、门禁、铁律 | 改它＝改整条主流程 |
| `references/` | 各角色指令文档（策略/写作/审核/设计/渲染/风格守卫…） | 改它＝改某个角色的行为 |
| `schemas/` | `slide_plan` / `style_lock` / `image_prompts` 的 JSON Schema（契约） | 改它＝改产物结构，需同步 references + scripts |
| `scripts/` | **纯 Python stdlib** 的校验/导出脚本（无 LLM、零依赖） | 改它＝改机器门禁逻辑 |
| `assets/` | 7 套风格的 preset JSON + 参考 CSS + 样例 deck | 改它＝改可选视觉资产 |
| `docs/` | 给人看的架构 / 为什么有效 | 不影响 Agent 运行 |

## 提交前请跑校验（确定性门禁）

脚本是纯 stdlib，`python3` 直接跑，无需装依赖：

```bash
python3 scripts/validate_html.py <deck>/index.html \
    --style-lock <deck>/source/style_lock.json \
    --slide-plan <deck>/source/slide_plan.json --json
python3 scripts/validate_slide_plan.py <deck>/source/slide_plan.json
python3 scripts/validate_context_lock.py <deck>/source/style_lock.json
```

`errors: []` 才算结构/视觉硬契约通过。CI 也会在 PR 上跑这套（见 `.github/workflows/`）。

## 几条原则

- **管线是串行 + 人工门禁**：改流程时别破坏"便宜的决策前置、昂贵的产出后置"这条主轴（见 [`docs/WHY-IT-WORKS.md`](docs/WHY-IT-WORKS.md)）。
- **零依赖优先**：`scripts/` 保持纯 stdlib，能跑在任意 agent/云端沙箱。重活（无头浏览器渲染、出图 backend）放在外层壳里，不进 skill。
- **别提交密钥**：`.env` 已被 `.gitignore` 拦截；出图 API key 只放本地 `.env`。
- **别提交生成产物**：`runs/`、`projects/`、`slide-deck/` 都是用户输出，已忽略。

## 提 Issue / PR

- Bug / 需求请走 [Issue 模板](.github/ISSUE_TEMPLATE)。
- PR 请说明：改了哪一层（SKILL/references/schemas/scripts/assets）、为什么、跑过哪些校验。
- 行为准则见 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)。

> 想要带界面的版本，见配套 Web 操作台 [`jumpx-ppt-studio`](https://github.com/JumpX-Labs/jumpx-ppt-studio)。
