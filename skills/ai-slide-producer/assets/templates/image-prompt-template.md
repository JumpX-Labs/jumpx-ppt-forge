---
slide_id: "{{slide_id}}"
slide_title: {{slide_title_yaml}}
filename: "{{filename}}"
visible_text:
  headline: {{visible_headline_yaml}}
  sub_headline: {{visible_sub_headline_yaml}}
  body:
{{visible_body_yaml}}
visual_composition: {{visual_composition}}
style_preset: "{{style_preset}}"
style_lock_ref: "source/style_lock.json"
negative_constraints:
{{negative_constraints_yaml}}
target_aspect_ratio: "{{target_aspect_ratio}}"
image_backend: "{{image_backend}}"
backend_model: "{{backend_model}}"
reference_image: "{{reference_image}}"
session_id: "{{session_id}}"
generated_image_path: "{{generated_image_path}}"
---

# Image Prompt — {{slide_id}} {{slide_title}}

## Slide Purpose

{{slide_purpose}}

## Exact Visible Text

- Headline: {{visible_headline}}
- Sub-headline: {{visible_sub_headline}}
{{visible_body_markdown}}

## Composition

{{composition_body}}

## Visual Hierarchy

{{visual_hierarchy}}

## Style Lock

- Preset: `{{style_preset}}`
- Aspect ratio: `{{target_aspect_ratio}}`
- Image style: {{image_style}}
- Density: {{density}}
- Palette: primary `{{primary_color}}`, accent `{{accent_color}}`, background `{{background_color}}`

## Negative Constraints

{{negative_constraints_markdown}}

## Backend

- Backend: `{{image_backend}}`
- Target image path: `{{generated_image_path}}`
