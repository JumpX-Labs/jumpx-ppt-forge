# QA Report

**Status**: pass
**Output Mode**: mixed
**Checked**: 2026-05-21

## Summary

- HTML builds successfully from `source/slide_plan.json` and `source/style_lock.json`.
- P04 and P07 embed local PNG files from `images/`.
- No unresolved content, visual, or delivery blockers in this sample.

## Content (Reviewer)

| Check | Status | Notes |
|-------|--------|-------|
| Main arc | pass | The sample explains Mixed output and closes with concrete checks. |
| Audience fit | pass | Written for product reviewers and implementers. |
| Critical issues | pass | none |

## Visual (Style Guard)

| Check | Status | Notes |
|-------|--------|-------|
| Style lock variables | pass | Editorial colors and fonts come from `style_lock.json`. |
| Preset fit | pass | Output reads as editorial-magazine. |
| Placeholders | pass | No `{{...}}` remains after build. |
| Image contract | pass | `images/slide-04.png` and `images/slide-07.png` are embedded. |
| Density / overflow | pass | Body counts stay within medium density limits. |

## Delivery (Producer)

| Check | Status | Notes |
|-------|--------|-------|
| Result visible | pass | `index.html` opens and contains local slide images. |
| Export tree | pass | Sample contains `index.html`, `images/`, `source/`, and `qa_report.md`. |
| README | pass | Sample README explains how to open and rebuild. |
| Manifest | pass | n/a for repository-local placeholder images. |

## Follow-ups

- none
