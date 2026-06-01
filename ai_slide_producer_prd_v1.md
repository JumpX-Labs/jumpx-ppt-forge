# PRD｜AI Slide Producer

版本:v1.0
日期:2026 年 5 月
状态:对外发布版本

---

## 0. 一句话定义

AI Slide Producer 是一个把粗糙输入变成可见 Slides 结果的 AI 生产系统——Image 与 HTML 双输出,每一步都有人工门禁,每页 Prompt 都是可复用资产。

---

## 1. 背景与问题

当前市面上多数 PPT / Slides 类 AI 工具存在以下问题:

- 结构过重,流程不清晰。
- 内部角色、流程、验收、生成方式没有被产品化。
- 把"输出文字建议"等同于"完成任务",用户看不到可见结果。
- 缺乏 Context Lock,长流程中风格和参数容易漂移。
- 缺乏中间态产出,生产链路不可编辑、不可复用。

AI Slide Producer 直接面向这些问题,以一套完整的角色 / 流程 / 门禁 / 风格锁 / 双输出系统,把"AI 做 PPT"从一次性请求变成可生产、可复用、可迭代的工作流。

---

## 2. 产品定位

### 2.1 产品名称

- 英文标识:`ai-slide-producer`
- 中文名:AI Slides 生产器

### 2.2 产品形态

> **One Skill, Multi-role Workflow**
>
> 一个主 Skill,内部多角色、多流程、多门禁、多输出路径。

设计选择依据:

- Slides 生产强依赖上下文一致性,一体化主 Skill 更易保持全局一致。
- 单一入口降低使用复杂度。
- 流程内部分层,长期可演进。

### 2.3 内部组织方式

> **流程为骨架,角色为能力。**

- 流程决定"按什么顺序推进"。
- 角色决定"每一步应用什么专业判断"。

---

## 3. 目标用户

### 3.1 核心用户

1. **内容创作者 / 讲师**
   高频制作课程课件、分享型 slides、公开演讲 deck。

2. **咨询顾问 / 企业培训师**
   把资料快速转化成结构化、有视觉表达的交付物。

3. **市场 / 产品 / 增长团队**
   制作产品发布、方案汇报、Campaign Proposal、复盘报告。

4. **AI 系统设计者**
   研究并复用一体化主 Skill 的设计模式。

### 3.2 非目标用户

不优先服务:

- 需要复杂表格和财务模型的传统 PPT 制作。
- 需要多人实时协作编辑的企业 PowerPoint 工作流。
- 需要 100% 严格遵循企业品牌手册的品牌设计生产。
- 需要直接替代专业设计师产出高端商业提案最终稿。

---

## 4. 核心用户需求

用户真正想要的不是:

> 给我一段 PPT 大纲。

而是:

> 帮我把一个主题、一组资料或一个想法,变成我能打开、能看、能展示、能继续修改的 slides 结果。

因此本产品必须满足:

1. 用户输入可以很粗糙。
2. 系统主动澄清关键变量。
3. 系统先产出可确认的大纲。
4. 系统将文字内容转为页面结构。
5. 系统提供视觉版本,而不只是文案。
6. 系统最终产出 HTML 或图片。
7. 用户可以基于结果继续迭代。

### 4.1 消费场景与输出形态解耦

本产品不预设"HTML 用于演讲,Image 用于传播"。

消费场景包括:现场演讲、课程教学、社群传播、自解释阅读、商业汇报、内部讨论、公开发布、个人作品集。

输出形态包括:Image Slides、Web / HTML Slides、Mixed(Image + HTML)。

核心原则:

> 不要用输出形态替用户决定消费场景。
>
> 系统可推荐,用户最终决定。

### 4.2 默认输出策略

当用户未明确指定输出形态时,系统采用:

> **Image-first**

依据:

- 用户最后看到的是直接可感知的视觉结果。
- 符合"不是文字建议,而是页面结果"的产品目标。
- 每页 Prompt 沉淀为可复用资产。

当图片生成 backend 不可用、生成失败或超出预算时,系统自动切换到 HTML 输出,并保留完整 Image Prompts 以便后续重生。

---

## 5. 产品范围

本节定义 v1.0 完整产品形态。所有列出的能力都是 v1.0 一等公民,不存在"进阶"或"待补充"路径。

### 5.1 支持的输入

1. 一个主题或想法。
2. 一段文字说明。
3. 一份课程 / 分享 / 汇报需求。
4. 粘贴的 Markdown / 笔记 / 文章。
5. 用户上传的参考资料摘要。
6. 用户指定的风格偏好。

完整的 PDF / DOCX / PPTX 解析不在 v1.0 范围内,可由前置工具处理后将提取的文本作为输入。

### 5.2 支持的输出

#### 5.2.1 Image Slides(默认)

一组图片:

- 每页一张 image。
- 默认比例 16:9,可切换 4:3 / 1:1 / 3:4 / 9:16。
- 每张图片基于同一 Style Lock 与 Design Spec 生成。
- 每张图片对应一个独立 Prompt 文件。

支持的图片生成 backend:

- Nano Banana / Gemini Image 系列
- OpenAI GPT Image 系列

#### 5.2.2 Web Slides

一个单页 HTML 文件:

- 横向翻页。
- 16:9 画布。
- 每页为一个 section / slide block。
- 支持键盘翻页与移动端基础浏览。
- CSS 风格系统内联或同目录引用。
- 本地可直接打开。

#### 5.2.3 Mixed Slides

同时输出:

- 一组 Image Slides。
- 一个 HTML Slides。
- HTML 中可嵌入生成图片。
- 完整的 Image Prompts、Style Lock、Slide Plan 全部保留。

---

## 6. 核心产品原则

### 6.1 最终结果优先

系统的最终交付不只是建议、大纲、文案、Prompt 或 Markdown,必须包含至少一种可见交付:

- 可打开的 HTML 文件
- 可查看的图片集
- 可继续加工的结构化文件

### 6.2 先确认,再放大

关键门禁:

- Brief 未确认,不进入大纲。
- 大纲未确认,不进入逐页内容。
- 风格未冻结,不进入批量视觉生产。
- 视觉规则未确认,不进入 HTML / Image 渲染。

### 6.3 流程可见,角色清楚

用户不需要理解所有内部细节,但系统内部必须始终清楚:

- 当前处在哪一步。
- 这一步由哪个角色负责。
- 本步输入是什么。
- 本步输出是什么。
- 是否需要用户确认。

### 6.4 Context Lock 防漂移

一旦用户确认以下信息,系统必须冻结:

- 主题
- 受众
- 页数范围
- 核心观点
- 叙事主线
- 视觉风格
- 颜色
- 字体
- 图片策略
- 页面节奏
- 禁区和硬约束

后续 HTML / Image 生成必须反复读取这些锁定参数。

### 6.5 Image-first,HTML 自动接管

默认产品策略:

> Image-first, HTML auto-takeover.

当用户未指定输出路径时,系统走 Image Slides。

当图片生成条件不满足(未提供图片生成 API、当前环境无法调用图片 backend、生成失败、超出预算),系统自动切换到 HTML Slides,并保留完整 Image Prompts,以便用户后续接入图片 backend 后从 Prompts 继续生成图片。

HTML 路径不是 Image 路径的"降级版本",而是产品的另一种一等输出形态。

### 6.6 输出形态不绑定消费场景

系统不假设 HTML 一定用于演讲、Image 一定用于传播、PPT 一定用于会议。

消费场景由用户设定,输出形态由用户选择。系统可基于场景推荐输出形态,但必须允许用户覆盖。

### 6.7 Prompt Archive 是核心资产

对于 Image 路径,每页最终 Image Prompt 必须落盘保存。

每页 Prompt 文件至少保存以下字段:

- Slide ID
- Slide Title
- Visible Text
- Visual Composition
- Style Preset
- Style Lock 引用
- Negative Constraints
- Target Aspect Ratio
- Image Backend
- Generated Image Path

核心判断:

> 图片是结果,Prompt 是资产。

### 6.8 支持中间态输出

系统不强制一次跑完整流程,支持以下中间态:

- `outline-only`:只生成大纲。
- `prompts-only`:只生成 Image Prompts。
- `images-only`:从已有 Prompts 生成图片。
- `html-only`:只生成 HTML。
- `regenerate`:指定页码局部重生。

中间态能力让系统从一次性生成器升级为可编辑、可复用、可局部返工的生产系统。

---

## 7. 信息架构

### 7.1 主 Skill 文件

`SKILL.md` 职责:

- 说明触发条件。
- 定义主 Workflow。
- 定义门禁。
- 定义角色切换。
- 定义输出路径。
- 指向 References / Templates / Scripts。

### 7.2 References

References 目录组织角色定义与流程规范:

```text
references/
  00-product-principles.md
  01-intake-brief.md
  02-context-pack.md
  03-strategist.md
  04-researcher.md
  05-writer.md
  06-reviewer.md
  07-designer.md
  08-web-renderer.md
  09-image-renderer.md
  10-style-guard.md
  11-producer.md
  12-style-presets.md
  13-regeneration-workflow.md
  14-quality-checklist.md
  15-export-contract.md
```

### 7.3 Assets

```text
assets/
  templates/
    web-slide-template.html
    web-slide-template-minimal.html
    image-prompt-template.md
  styles/
    teaching-clean.css
    swiss-system.css
    magazine-editorial.css
    blueprint.css
    sketch-notes.css
    corporate.css
    creator-social.css
  style-presets/
    teaching-clean.json
    swiss-system.json
    editorial-magazine.json
    blueprint.json
    sketch-notes.json
    corporate.json
    creator-social.json
  examples/
    example-context-pack.md
    example-outline.md
    example-slide-plan.md
    example-image-prompts.md
```

风格系统采用参数化设计,每套 Style Preset 拆解为以下维度:

- `texture`
- `mood`
- `typography`
- `density`
- `color_palette`
- `layout_bias`
- `image_style`
- `negative_constraints`

#### 命名约定

- 程序标识符使用 `kebab-case`:`teaching-clean`、`swiss-system`。
- 用户展示名使用 Title Case:`Teaching Clean`、`Swiss System`。

### 7.4 Scripts

```text
scripts/
  build_html.py
  validate_slide_plan.py
  validate_context_lock.py
  export_images_manifest.py
  regenerate_slide.py
```

---

## 8. 内部角色设计

### 8.1 Strategist

职责:

- 判断任务目标。
- 判断受众。
- 判断使用场景。
- 设计叙事主线。
- 生成 Deck Strategy。

输出:

- Project Brief
- Narrative Strategy
- Page Count Recommendation
- Content Arc

### 8.2 Researcher / Synthesizer

职责:

- 整理输入材料。
- 提取关键观点。
- 压缩冗余信息。
- 标注必要信息与可选信息。

输出:

- Knowledge Pack
- Key Claims
- Evidence List
- Forbidden / Sensitive Points

### 8.3 Writer

职责:

- 生成每页标题。
- 写页面正文。
- 写讲解提示。
- 控制信息密度。
- 保持表达风格一致。

输出:

- Slide Copy
- Speaker Notes
- On-slide Text

### 8.4 Reviewer

职责:

- 检查逻辑链路。
- 检查事实一致性。
- 检查重复和遗漏。
- 检查是否符合受众。
- 检查是否过度承诺。

输出:

- Review Notes
- Required Changes
- Approval / Rework Decision

### 8.5 Designer

职责:

- 定义视觉风格。
- 定义字体、颜色、布局规则。
- 判断每页适合的视觉结构。
- 输出 Visual Spec。

输出:

- Design Spec
- Layout Strategy
- Style Lock

### 8.6 Web Renderer

职责:

- 将 Slide Plan 转为 HTML。
- 使用模板和 CSS 构建页面。
- 保证每页在浏览器可见。
- 支持翻页交互。

输出:

- `index.html`

### 8.7 Image Renderer

职责:

- 将每页 Slide Plan 转为 Image Prompt。
- 将每页最终 Prompt 写入 `prompts/` 目录。
- 调用图片生成 backend 生成图片。
- 保持每页风格一致。
- 支持从已有 Prompts 继续生成图片。
- 支持局部重生指定页面。
- 生成图片清单。

输出:

- `prompts/01-slide-cover.md`
- `prompts/02-slide-problem.md`
- `images/slide-01.png`
- `images/slide-02.png`
- `images/manifest.json`

硬规则:

> 如果用户选择 Image 路径,必须使用真实图片生成 backend。不允许用 HTML、SVG、Canvas 或代码渲染伪装成 Image Slides。

如果无法调用图片 backend:

- 保留所有 Prompts。
- 自动切换到 HTML 路径。
- 告知用户后续可基于 Prompts 继续生成图片。

### 8.8 Style Guard

职责:

- 在 Web Renderer / Image Renderer 输出后做风格一致性检查。
- 对照 Style Lock 验证每页输出。
- 识别颜色漂移、字体漂移、版式不一致、图标风格不一致。
- 在 v1.0 中作为 Quality Check 阶段的核心检查者。

输出:

- Style Compliance Report
- Detected Drifts
- Required Re-render Decisions

与 Reviewer 的区别:Reviewer 检查内容质量,Style Guard 检查视觉与风格合规。

与 Producer 的区别:Producer 负责最终交付组装,Style Guard 负责输出前的风格守门。

### 8.9 Producer

职责:

- 最终检查。
- 文件命名。
- 输出目录整理。
- 生成交付说明。

输出:

- Final Delivery Folder
- Export Contract
- User-facing Result

---

## 9. 主 Workflow

### Step 1:Intake / 需求澄清

输入:用户给出的主题、资料、目标或想法。

必须澄清:

1. 这份 slides 的使用场景是什么?
2. 受众是谁?
3. 希望讲多长时间?
4. 预计多少页?
5. 用户已有材料是什么?
6. 想要什么风格?
7. 最终想要 Web、Image,还是 Mixed?
8. 有没有必须出现或不能出现的内容?

输出:`project_brief.md`

门禁:用户确认 Brief 后才能进入 Step 2。

---

### Step 2:Context Pack / 上下文资产包

将散乱材料整理成固定结构:

```text
Project Goal
Audience
Use Case
Knowledge Base
Narrative Direction
Design Direction
Tone Rules
Forbidden Zones
Acceptance Criteria
Output Mode
```

输出:`context_pack.md`

门禁:Context Pack 生成后,必须显示摘要供用户确认。

---

### Step 3:Outline / 叙事大纲

基于 Context Pack 生成大纲。

默认叙事结构:

```text
Hook → Context → Core → Shift → Takeaway
```

可根据场景切换:

- **教学课件**:问题 → 概念 → 方法 → 示例 → 练习 → 总结
- **商业汇报**:背景 → 问题 → 洞察 → 方案 → 路径 → 决策
- **产品发布**:痛点 → 新机会 → 产品 → 价值 → Demo → 行动
- **咨询方案**:现状 → 诊断 → 框架 → 建议 → 路线图 → 风险

输出:`outline.md`

门禁:大纲未确认,不进入逐页内容生成。

---

### Step 4:Slide Plan / 页面计划

将大纲转为逐页计划。每页必须包含:

```text
page_id
page_title
page_goal
page_role_in_story
key_message
on_slide_text
speaker_notes
visual_direction
layout_type
image_requirement
```

输出:`slide_plan.json` 或 `slide_plan.md`

门禁:页面计划必须通过结构检查后,自动进入 Step 5。

---

### Step 5:Narrative Review / 内容审核

Step 4 完成后,Reviewer 自动触发,无需用户手动启动。

检查:

- 是否有清晰主线。
- 每页是否承担不同功能。
- 页面之间是否衔接。
- 是否重复。
- 是否遗漏关键观点。
- 是否符合受众理解程度。
- 是否有未经验证的事实或过度承诺。

输出:`review_report.md`

门禁:严重问题必须返工,不能进入视觉生产。

---

### Step 6:Design Spec / 视觉规格

定义全局视觉系统:

```text
canvas_ratio
style_name
font_system
color_palette
layout_rules
image_style
icon_style
chart_style
motion_rule
page_density_rule
```

输出:

- `design_spec.md`:人类可读说明。
- `style_lock.json`:机器执行参数。

门禁:风格未确认,不进入 Web / Image 渲染。

---

### Step 7A:Image Render / 图片生成(默认)

适用条件:

- 用户选择 Image 输出。
- 用户未指定输出形态时的默认路径。
- 用户希望先看到视觉完成度最高的结果。

输入:

- Slide Plan
- Design Spec
- Style Lock
- Image Prompt Template
- Style Preset

输出:

- 每页一张图片
- `prompts/`
- `image_prompts.md`
- `images_manifest.json`

图片生成提供两个 backend 路径:Nano Banana / Gemini Image,或 OpenAI GPT Image。

注意:

- 图片生成不应直接输入整份长文档。
- 每页 Image Prompt 必须从 Slide Plan 和 Style Lock 派生。
- 所有图片必须遵守同一风格系统。
- 每页 Prompt 必须先落盘,再调用生成。
- 如果某页包含大量文字,需提示用户图片文字稳定性风险,并建议改为更少文字或切换到 HTML 路径。

### Step 7B:Web Render / HTML 生成

适用条件:

- 用户选择 Web 输出。
- 图片生成 backend 不可用时的自动接管路径。
- 用户希望获得可打开、可修改、可阅读的单页 HTML。

输入:

- Slide Plan
- Design Spec
- Style Lock
- HTML Template

输出:

- `index.html`

要求:

- 单页 HTML。
- 横向翻页。
- 16:9 画布。
- CSS 内联或同目录可引用。
- 不依赖复杂构建工具。
- 页面可直接本地打开。

验收:

- 每页可见。
- 没有明显文本溢出。
- 风格一致。
- 页面顺序正确。
- 封面、章节页、正文页、总结页结构完整。

### Step 7C:Intermediate Output / 中间态输出

系统支持不完整跑完整流程,而是停在用户需要的中间层。

支持模式:

```text
outline-only
prompts-only
images-only
html-only
regenerate slide N
regenerate slides N, M, K
```

中间态能力让用户可以先审核 Prompts,再决定是否生成图片;可以只重生不满意的页面;可以切换图片 backend 而不重做内容。

---

### Step 8:Quality Check / 质量检查

由 Style Guard 和 Reviewer 共同执行。

#### 内容检查(Reviewer)

- 主线是否完整。
- 每页是否有独立作用。
- 标题是否有表达力。
- 是否有事实风险。

#### 视觉检查(Style Guard)

- 是否统一风格。
- 是否有文字溢出。
- 是否有视觉拥挤。
- 是否有颜色漂移。
- 是否有字体漂移。

#### 交付检查(Producer)

- HTML 是否可打开。
- 图片是否全部生成。
- 文件命名是否正确。
- 是否包含 manifest。
- 用户是否能直接看到结果。

输出:`qa_report.md`

门禁:严重问题必须返工。

---

### Step 9:Delivery / 交付

最终交付结构:

```text
project-name/
  index.html
  images/
    slide-01.png
    slide-02.png
  source/
    context_pack.md
    outline.md
    slide_plan.md
    design_spec.md
    style_lock.json
  prompts/
    01-slide-cover.md
    02-slide-problem.md
  qa_report.md
  README.md
```

如果只选择 Web:

```text
project-name/
  index.html
  source/
  qa_report.md
  README.md
```

如果只选择 Image:

```text
project-name/
  images/
  prompts/
  images_manifest.json
  source/
  qa_report.md
  README.md
```

---

## 10. Web 版本规格

### 10.1 画布

- 默认:16:9
- 推荐尺寸:1920 × 1080 或响应式缩放

### 10.2 交互

- 键盘左右键翻页
- 页面指示器
- 移动端滑动
- ESC 缩略图索引

### 10.3 页面类型

至少支持:

1. Cover
2. Section Divider
3. Big Idea
4. Two Column
5. Quote / Statement
6. Framework
7. Timeline / Process
8. Comparison
9. Image + Text
10. Closing

### 10.4 风格预设

v1.0 提供 7 套 Style Presets:

1. **Teaching Clean** (`teaching-clean`)
   教学课件,清楚、留白、层级明显。

2. **Swiss System** (`swiss-system`)
   网格、信息密度、理性表达。

3. **Editorial Magazine** (`editorial-magazine`)
   大标题、图片、强叙事感。

4. **Blueprint** (`blueprint`)
   蓝图风格,适合产品发布、技术架构。

5. **Sketch Notes** (`sketch-notes`)
   手绘感、轻松、适合分享传播。

6. **Corporate** (`corporate`)
   商务汇报,稳重、专业、克制。

7. **Creator Social** (`creator-social`)
   适合社群分享、个人 IP、短视频脚本配套。

---

## 11. Image 版本规格

### 11.1 目标

生成用户可直接查看的视觉页面,而非文字描述。

### 11.2 图片比例

- 默认:16:9
- 可选:4:3 / 1:1 / 3:4 / 9:16

### 11.3 每页 Image Prompt 结构

```text
Slide purpose
Exact visible text
Composition
Visual hierarchy
Style lock
Color palette
Typography direction
Image / icon direction
Negative constraints
Aspect ratio
```

### 11.4 文本策略

图片生成对文字稳定性存在风险:

- 标题文字可进入图片生成。
- 大段正文不建议依赖图片模型生成。
- 复杂中文正文优先走 HTML 路径。
- 必须图片化时,单页文字必须极少。

### 11.5 双版本推荐策略

针对不同消费场景的推荐:

- **教学类 slides**:HTML 优先,Image 用于封面与金句页。
- **传播类 slides**:Image 优先,HTML 作为完整版备份。
- **混合场景**:Mixed 输出,HTML 引用生成图片。

---

## 12. Context Lock 设计

`style_lock.json` 示例:

```json
{
  "deck_title": "从 Prompt 到 Skill",
  "audience": "AI 课程学员",
  "canvas_ratio": "16:9",
  "style_name": "teaching-clean",
  "primary_color": "#111827",
  "accent_color": "#2563EB",
  "background_color": "#F9FAFB",
  "font_heading": "Inter / Noto Sans SC",
  "font_body": "Inter / Noto Sans SC",
  "image_style": "clean educational diagram",
  "density": "medium-low",
  "forbidden": [
    "不要一上来讲 Agent",
    "不要把 PPT 自动化讲成画几页图",
    "不要让页面塞满文字"
  ]
}
```

使用规则:

- Web Renderer 每次渲染必须读取。
- Image Renderer 每页 Prompt 必须读取。
- Reviewer 检查时必须对照。
- Style Guard 检查时必须对照。
- 用户修改风格时,必须更新 `style_lock`,而不是临时覆盖。

---

## 13. 门禁设计

### Gate 1:Brief Confirmed

用户是否确认:

- 受众
- 场景
- 目标
- 页数
- 输出形态

### Gate 2:Outline Confirmed

用户是否确认:

- 章节顺序
- 页面数量
- 叙事主线

### Gate 3:Content Approved

Reviewer 是否通过:

- 逻辑
- 表达
- 事实
- 节奏

### Gate 4:Style Locked

用户是否确认:

- 风格
- 色彩
- 字体
- 图片策略
- 页面密度

### Gate 5:Style Compliance

Style Guard 是否通过:

- 每页是否守住 Style Lock
- 是否存在颜色 / 字体 / 版式漂移
- 是否需要局部重生

### Gate 6:Result Visible

最终是否产生:

- 可打开的 HTML,或
- 可查看的图片,或
- 二者都有

---

## 14. 被调度接口

本 Skill 设计为可被 Agent 自动调度。

### 14.1 触发关键词

`description` 字段必须包含以下触发场景:

- "做一份 PPT" / "做一个 deck" / "做几页 slides"
- "生成课件" / "做汇报"
- "做产品发布材料" / "做演讲 slides"
- "把这份资料变成 PPT"

### 14.2 参数提取顺序

Agent 调度时,系统按以下顺序提取参数:

1. **主题**(必需)
2. **受众**(可推断,可询问)
3. **页数**(可默认 8-12 页)
4. **风格**(可默认 `teaching-clean`)
5. **输出形态**(可默认 Image-first)
6. **特殊约束**(可推断,可询问)

### 14.3 状态机

系统对外暴露以下状态,可被 Agent 感知:

```text
brief → outline → plan → review → spec → render → qa → delivery
```

每个状态可被 Agent 查询当前进度,用于判断:

- 当前所在阶段。
- 下一步需要的输入。
- 是否处于等待用户确认的状态。
- 是否可以局部重生。

### 14.4 中间产物 Schema

为支持 Agent 编排,所有中间产物使用统一 schema 命名:

- `project_brief.md`
- `context_pack.md`
- `outline.md`
- `slide_plan.json`
- `design_spec.md`
- `style_lock.json`
- `image_prompts.md`
- `review_report.md`
- `qa_report.md`

Agent 可读取任意中间产物,基于其判断下一步动作。

---

## 15. 用户路径

### 路径 A:Web 优先

用户输入:

> 帮我做一套 8 页的 AI 课程介绍 slides,风格清爽,最后给我 HTML。

系统执行:

1. 提出 2-3 个关键澄清问题。
2. 生成 Brief。
3. 生成 Outline。
4. 等待用户确认。
5. 生成 Slide Plan。
6. 生成 Design Spec。
7. 生成 HTML。
8. 输出可打开结果。

### 路径 B:Image 优先

用户输入:

> 帮我生成一组适合发布到社群的 AI PPT 图片,每页一张图。

系统执行:

1. 确认主题、页数、风格。
2. 生成 Slide Plan。
3. 生成 Image Prompts。
4. 调用图片模型。
5. 输出图片结果。

### 路径 C:Mixed

用户输入:

> 我想要一套可以讲课的 HTML slides,同时生成几张封面和金句图。

系统执行:

1. Web 路径生成完整 HTML。
2. Image 路径仅为封面、章节页、金句页生成图片。
3. HTML 中引用这些图片。
4. 用户同时获得可讲课版本和传播图版本。

### 路径 D:中间态使用

用户输入:

> 我已经有大纲了,直接生成图片 Prompts,先不要出图。

系统执行:

1. 跳过 Step 1-3。
2. 从用户提供的大纲生成 Slide Plan。
3. 生成 Design Spec 与 Style Lock。
4. 生成 Image Prompts 并落盘。
5. 不调用图片生成 backend。
6. 用户审核 Prompts 后,再决定是否进入图片生成。

---

## 16. 成功标准

### 16.1 用户视角

用户使用本产品后,应能获得:

- 一份结构清楚的 Deck。
- 一个可打开的 HTML,或
- 一组可查看的 Slide Images,或
- Mixed 输出。
- 而不是一堆"建议"。

### 16.2 产品视角

产品成功的标志:

1. 任意 5-20 页 Slides 可稳定生成。
2. HTML 可打开、可翻页、风格一致。
3. Image 路径可生成至少封面 / 金句页 / 概念页。
4. 用户最终可见结果。
5. 生产过程可解释、可复盘、可迭代。
6. 中间产物全部可读、可修改、可复用。
7. 任意一页可局部重生。
8. 可被 Agent 调度并按状态机推进。

---

## 17. 本 PRD 的最终判断

最终架构选择:

> 外部一个 Skill,内部多角色 Workflow。
> Image-first,HTML 自动接管。
> 用户最终看到结果,不是文字。
> Skill 的价值不是一次生成,而是长期可复用的生产系统。

---

## 附录 A:参考样本分析

本 PRD 在设计阶段分析了三个具有代表性的 PPT / Slides 类 AI 工具。它们的封装方式不同,但共同揭示了一个核心事实:

> 优秀的 PPT 类 AI 工具不是一段提示词,而是一套被封装的生产系统。

### A.1 样本 1:guizang-ppt-skill

特点:

- 产物明确:横向翻页网页 PPT,单 HTML 文件。
- 风格明确:提供"电子杂志 × 电子墨水"和"瑞士国际主义"两套风格。
- 场景明确:适合分享、演讲、发布会、Demo Day 等强表达场景。
- 边界明确:不适合大段表格数据、培训课件、多人协作编辑。
- 开工前有需求澄清机制:风格、受众、时长、素材、图片、主题色、硬约束。
- 用户无大纲时,使用叙事弧组织内容:Hook → Context → Core → Shift → Takeaway。
- 有模板、主题色、布局、图片规范和硬规则。
- 最终交付物是可运行的 HTML Slides。

本 PRD 采纳的设计原则:

1. 输出必须可见——最终给用户的是 HTML 页面或图片,而不是 PPT 大纲。
2. 风格必须被锁定——一套 Deck 只能使用一套风格系统。
3. 开工前必须澄清关键变量——否则后期返工成本极高。
4. 图片和截图必须进入生产流程——不能把视觉当成最后补充。
5. 一体化 Skill 内部可以拥有完整 Workflow。

### A.2 样本 2:ppt-master

特点:

- 产物明确:将 PDF / DOCX / URL / Markdown 等源材料转换成 SVG 页面,并导出 PPTX。
- 流程明确:Source Document → Create Project → Template Option → Strategist → Image_Generator → Executor → Post-processing → Export。
- 有严格执行纪律:必须串行执行,Blocking 步骤等待用户确认,不能跨阶段打包执行。
- 有 Gate 机制:每一步进入前必须检查前置条件。
- 有角色切换:Strategist、Image_Generator、Executor 等角色有不同职责。
- 有 Context Lock:每页生成前必须重新读取 `spec_lock`,避免长流程中的颜色、字体、图标、图片漂移。
- 有质量检查脚本:SVG 生成后必须检查错误,修复后才能继续。
- 有导出流程:后处理、拆分 Notes、导出 PPTX。

本 PRD 采纳的设计原则:

1. Workflow 不是步骤列表,而是带 Gate 的推进系统。
2. 自动化不是全程不停,而是在关键节点必须停。
3. 长流程任务必须有 Context Lock,防止风格和执行参数漂移。
4. 成熟系统需要区分人类可读设计说明和机器可执行参数。
5. 当任务足够复杂,系统会从提示词变成小型生产软件包。

### A.3 样本 3:baoyu-slide-deck

特点:

- 产品定位清楚:把内容转成专业 Slide Deck Images,不为现场演讲服务,而是为阅读、分享、自解释和社交传播服务。
- 最终输出以 Raster Images 为核心,每页一张图,再合并成 PPTX / PDF。
- 不接受用 SVG、HTML、Canvas 等代码渲染替代图片生成——如果决定走图片路线,必须真正调用图片生成 backend。
- 每页 Image Prompt 保存为独立 Prompt 文件,作为可复现记录,也方便切换图片 backend。
- 支持 outline-only、prompts-only、images-only、regenerate specific slides 等中间态。
- 有 17 套 Style Presets,每套拆成 texture / mood / typography / density 四个维度。
- 支持内容信号自动选择风格,根据源文本长度估算推荐页数。
- 有明确确认策略:默认生成前必须确认,除非用户明确说"直接生成"。
- 有文件布局规范、备份规则、图片合并脚本和修改工作流。

本 PRD 采纳的设计原则:

1. 先定义消费场景——同样是 Slides,面向"阅读分享"和面向"现场演讲"的设计原则不同。
2. 图片路径要有强约束——如果选择 Image 输出,不能用 HTML / SVG 假装图片生成。
3. Prompt 文件是资产——每页 Prompt 必须落盘,成为可复现、可修改、可切换 backend 的生产记录。
4. 中间产物要可停可复用——`outline-only`、`prompts-only`、`images-only` 是必要的产品能力。
5. 风格系统要参数化——Preset 之外,应拆成 texture / mood / typography / density 等可组合维度。
6. 局部返工是一等能力——成熟 Deck 生产不是一次生成,而是编辑、重生、合并、导出。

### A.4 三个样本提炼出的共同结构

不管是一体化 Skill 还是分离式 Skill,一个成熟的 AI Slides 系统通常包含以下 8 个组成部分:

1. **定位**:做哪类 Slides,最终产物是什么。
2. **边界**:适合什么,不适合什么。
3. **输入**:用户需要提供什么材料,系统主动澄清什么变量。
4. **流程**:先做什么,后做什么,何时停、何时继续。
5. **风格**:字体、颜色、版式、视觉语言、Style Lock。
6. **资源**:HTML 模板、Layout 库、Examples、Assets、Style Presets。
7. **检查**:内容、视觉、风格、代码、导出的多维质量检查。
8. **交付**:HTML / Image / PPTX / PDF 等可见结果与配套中间产物。

本 PRD 以这 8 个共性作为产品骨架。

---

文档版本:v1.0
状态:对外发布
