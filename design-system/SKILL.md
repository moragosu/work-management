---
name: seolbihyeoksin-design
description: Use this skill to generate well-branded interfaces and assets for the 설비혁신파트 협업 시스템 (Facility-Innovation Part Collaboration System) — an internal Korean OKR & weekly-progress management tool — either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Quick map
- `README.md` — product context, content voice, visual foundations, iconography, and a full file index. **Start here.**
- `colors_and_type.css` — all design tokens (color, type, spacing, radius, shadow, layout) as CSS variables + semantic type classes. Import this first in any new file.
- `assets/logo-mark.svg` — the bullseye/target brand mark (`currentColor`).
- `preview/` — specimen cards showing each token group and component.
- `ui_kits/work-management/` — interactive recreation of the app + reusable React components (`kit.css`, `Primitives.jsx`, `Shell.jsx`, view files). Lift components from here.

## Essentials (so you don't have to re-derive them)
- **Language:** Korean, professional/operational, polite-formal (-습니다). Imperative verb labels (저장·취소·삭제·등록). Counts use 건/명. Emoji only in positive empty states (👍).
- **Color:** primary `#1e36b1`, navy sidebar `#0d1772`, cool canvas `#f0f4f8`, white surfaces. Conventional green/red/amber semantics. No hero gradients.
- **Type:** Pretendard (CDN), small & dense — 15px body, 11–12px labels/badges, 30px KPI numbers. `word-break: keep-all` for Korean.
- **Icons:** Material Symbols Outlined (CDN), outlined/regular by default, FILL 1 for emphasis. Don't introduce a second icon family or hand-draw icons.
- **Shape:** small radii (2–4px controls, 8px cards, full pills/badges), hairline `#e5e7eb` borders, soft 4-step shadow scale, purposeful colored left-accent borders. Fast 0.12–0.2s transitions; no bounces.
