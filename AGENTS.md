# AGENTS.md

本仓库是一个 **Agent Skill**（AI PPT Forge）。它的"入口大脑"是 [`SKILL.md`](SKILL.md)——触发词、九步管线、人工门禁、铁律、状态机全在那里。

**给任何 coding agent（Claude Code / Cursor / Codex / 自建）的指令：**

1. 先完整读 [`SKILL.md`](SKILL.md)，按其管线执行。
2. 各角色细则在 [`references/`](references/)，进入对应步骤前读对应文档。
3. 契约见 [`schemas/`](schemas/)；机器校验见 [`scripts/`](scripts/)（纯 stdlib，可直接 `python3` 跑）。
4. 别提交密钥（`.env`）与生成产物（`runs/`、`projects/`）。

> 想了解它怎么搭、为什么有效：[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [`docs/WHY-IT-WORKS.md`](docs/WHY-IT-WORKS.md)。
