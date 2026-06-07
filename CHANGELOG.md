# Changelog

本项目的所有重要变更都记录在此。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循 [SemVer](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Changed
- 拓宽 CJK 字体兜底栈（+ Microsoft YaHei / Hiragino Sans GB / Source Han Sans），裸 HTML 在 Win/旧 Mac/安卓上也有合理字形。
- README 升级为发布级（头部 / 徽章 / 导航 / 风格画廊位 / 训练营 CTA）。
- 新增 OSS 健康文件：`LICENSE`(MIT)、`CONTRIBUTING`、`CODE_OF_CONDUCT`、`AGENTS`、`CREDITS`、`.github/`（issue/PR 模板 + CI）。

## [1.1.0] - 2026-06-07

### Added
- **确定性 QA 测量门禁**：`scripts/validate_html.py` 从"结构解析器"升级为测量引擎——
  - 外链 / 非自包含检测（强制"禁外链"硬契约）；
  - 页序、`data-page-id`、`data-layout` 与 `slide_plan` 一致性（专治 regeneration 后的漂移）；
  - `style_lock` 必备色使用 + 保守的"外来色"漂移（状态/派生色不误报）；
  - 每页 list 项数 / 文本量预算（溢出粗代理）；
  - `--json`（给 regeneration 循环消费）与 `--strict`。
- Step 8 / Style Guard 定下"**机器判定即权威 + 收敛规则**"：`failed:false` 即停，不得再凭肉眼把已通过的页拖回返工——根治 QA 反复返工。

### Note
- 真实像素溢出 / WCAG 对比度 / 断图属 **Tier-1 渲染检查**，由外层壳（无头浏览器）执行；skill 本体保持零依赖。

## [1.0.0] - 2026-06-01

### Changed
- **彻底移除模板渲染器**：模型按设计 token 直接写 HTML 成为唯一渲染路径，质量上限不再被模板封顶。

### Added
- 九步串行管线 + 人工门禁（确认大纲 / 选风格 / 选输出形态）；
- 三套 JSON Schema 契约（`slide_plan` / `style_lock` / `image_prompts`）；
- 7 套内置视觉风格 preset；双输出（HTML / AI 配图）；过程即资产（全中间产物落盘）。

[Unreleased]: https://github.com/JumpX-Labs/jumpx-ppt-forge/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/JumpX-Labs/jumpx-ppt-forge/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/JumpX-Labs/jumpx-ppt-forge/releases/tag/v1.0.0
