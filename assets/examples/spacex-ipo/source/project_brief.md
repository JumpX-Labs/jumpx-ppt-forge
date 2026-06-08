# Project Brief — 上市的，不是火箭

| 字段 | 值 |
|------|----|
| 主题 | SpaceX 下周上市，史上最大 IPO——但重点不是火箭 |
| 场景 | 对外观点输出 / 演讲开场 / 社媒长图 |
| 受众 | 关注科技与投资的泛财经读者；想看懂这场 IPO 真正逻辑的人 |
| 时长/页数 | 6 页（紧凑观点弧） |
| 风格 | `editorial-magazine`（暖纸 + 墨色衬线大标题 + 单一品牌红 accent） |
| 输出形态 | `html-only`（16:9，可本地打开/导出 PDF） |
| 核心论点 | 重点不是火箭，是 **Starlink**——把一次性发射转化为全球经常性订阅现金流的"收费站"；这次 IPO 真正的历史意义是太空第一次作为"现金流生意"被公开市场定价 |

## Output Mode 决议
- 用户语境：要"用 ppt skill 生成一个 deck" → 走 HTML 路径。
- 未要求配图、本会话不假设可用出图 backend → **`html-only`**。图片 Prompt 不落盘（纯 HTML 渲染）。

## 硬约束 / Forbidden Zones
- 不编造未经证实的 2026 精确财务数字（估值/营收/订户具体数）当事实；模型逻辑示意必须标注。
- 全内联自包含，禁外链。
- 不堆等大灰卡片网格（editorial preset 的 `negative_constraints` 已并入 `style_lock.forbidden[]`）。

> 这是一份**观点 deck**：论点本身就是产物。论点可被替换（见 outline 的"可替换的真正重点"）。
