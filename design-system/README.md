# 설비혁신파트 협업 시스템 — Design System

> _Facility-Innovation Part Collaboration System_ — an internal **OKR & weekly-progress** management tool for a Korean manufacturing/engineering team ("설비혁신파트", a Facility Innovation Part).

This design system captures the visual language, tokens, copy voice, and UI components of the application so that designers and agents can produce on-brand interfaces, mockups, and production code.

---

## 1. Product Context

**What it is.** A web app where a team plans **목표(Objectives)** and **Key Results**, breaks them into **과제(tasks)** and **소과제(sub-tasks)**, and runs a **weekly cadence**: every week each task owner registers progress/issues (진행 현황 및 이슈), links a Confluence page, and answers questions raised by teammates and leaders. A dashboard rolls all of this up into KPIs, a per-member activity table, and a week-by-week registration matrix.

**Who uses it.** A single part/team. Roles are `member` / `group_leader` / `part_leader`, plus an `is_admin` flag. Leaders review progress and tag people with questions; members answer and log issues. Korean is the sole UI language.

**Core surfaces (routes):**
| Route | Korean label | Purpose |
|---|---|---|
| `/dashboard` | 대시보드 | KPIs, part notice, action panels (questions/issues), member-activity table, weekly registration matrix, objective cards |
| `/progress` | 주간 진행 현황 | The weekly workhorse: last-week / this-week panels, per-task issue threads + Q&A, Confluence links |
| `/admin` | 관리 도구 | Manage objectives, tasks/sub-tasks, staff |
| `/feedback` | 피드백 | Feedback board |
| `/help` | 도움말 | In-app help/guide |
| `/login`, `/signup`, `/change-password` | 로그인 등 | Auth (forced password change on first login) |

**Tech stack.** Vue 3 + Vite + Pinia (frontend), FastAPI + SQLite (backend). Rich text via Tiptap. Icons via Material Symbols. (Note: `AGENTS.md` in the repo references an aspirational SvelteKit/Samsung-One direction, but the **shipped code is Vue + Pretendard + Material Symbols** — that is the source of truth used here.)

### Sources
- **GitHub:** https://github.com/moragosu/work-management — explore further (especially `frontend/src/style.css`, `frontend/src/App.vue`, and the `views/` + `components/` folders) to build higher-fidelity designs.
  - Design tokens lifted from `frontend/src/style.css`.
  - Layout/shell from `frontend/src/App.vue`; screens from `frontend/src/views/*.vue`.

---

## 2. Content Fundamentals

**Language & audience.** 100% **Korean**, written for an internal engineering team. Tone is **professional, concise, operational** — this is a tool to get weekly work logged, not a consumer product. No marketing fluff.

**Voice & address.** Largely **impersonal / system-voice**. UI labels are bare nouns (대시보드, 피드백, 관리 도구). Actions are imperative verbs in the polite-formal register: 저장, 취소, 삭제, 수정, 등록, 새로고침, 로그인. Helper/empty text uses the **합쇼체 / -습니다** polite-formal ending:
- "등록된 목표가 없습니다. 관리 도구에서 목표를 추가하세요."
- "아직 답변이 없습니다."
- "링크가 복사되었습니다"
- "이슈를 삭제하시겠습니까?" (confirm dialogs ask, don't command)

**Casing & spacing.** Korean has no casing; **English/Latin tokens stay as-is** (Key Results, Confluence, OKR, W21). Counts use the Korean counter **건** ("3건" = 3 items), people use **명** ("파트원 5명").

**Micro-labels.** Tiny uppercase Latin labels appear for structural English terms only (e.g. table headers via `text-transform: uppercase`, "Key Results"). Korean labels are never uppercased.

**Emoji.** **Used sparingly, only in positive empty/affirmation states** — e.g. "미답변 의견/질문이 없습니다 👍" and "등록된 진행 현황 및 이슈가 없습니다 👍". The favicon is 📊. Never use emoji as functional iconography (that's Material Symbols' job).

**Week notation.** ISO-style `2026-W21` internally; display strips the current year to `W21` and renders ranges like `5/18 – 5/24`. "지난주 / 이번주" (last week / this week) toggles are everywhere.

**Vibe.** Calm, data-dense, trustworthy "internal ops dashboard." Lots of small badges and pills carrying status and metadata; short truncated previews that expand into modals. The personality comes from **tidy structure and a confident navy/blue palette**, not decoration.

---

## 3. Visual Foundations

**Palette & mood.** A disciplined **navy-and-blue** system on a cool blue-gray canvas. `--primary #1e36b1` carries all action/links/active states; the sidebar is the deep `--secondary #0d1772`. The app canvas is `--bg-main #f0f4f8` (never pure white) with white `--surface` cards floating on top. Semantic colors are conventional: green success, red danger, amber/orange warning. A small **chart palette** (sky, purple, orange, green, yellow, slate) handles data viz. **No purple/blue hero gradients** — the only gradients are the small logo badge (`135deg #4a6cf7→#1a32c8`) and user avatar (`#2563eb→#7c3aed`).

**Typography.** **Pretendard** (Korean-optimized sans) throughout, with Malgun Gothic / system fallbacks. Type is **small and dense** — 15px body, 14px controls, 11–12px for the abundant labels/badges. Headings are 16–20px **700**. Big KPI numbers are 30px/700 with tight `-0.02em` tracking. Structural English labels and table headers are uppercased with letter-spacing. Long-form text uses `word-break: keep-all` (Korean line-breaking) and 1.6–1.7 line-height.

**Spacing & layout.** 4-based scale (4/8/16/24/32/48). Fixed **224px navy sidebar** + **56–60px white top bar**, content on a scrollable canvas with 32px page padding. Heavy use of CSS grid (`grid-2`, `grid-3`, `grid-4`) with `gap`. Dense tables with sticky first columns for the weekly matrix.

**Backgrounds.** Flat color only — `--bg-main` canvas, white surfaces. **No imagery, no textures, no patterns, no full-bleed photos.** Tinted "soft" fills denote semantics: `--primary-light` blue, `#fff7ed` orange issue boxes, `--success-light` green, etc.

**Corners (radius).** Buttons/inputs are **small** (2–4px), cards/nav/modals are 8px, big modals & the auth card are 12px, the logo badge 10px. Badges, pills, avatars, and progress bars are fully round (`9999px`).

**Borders.** Hairline `1px solid --outline (#e5e7eb)` on cards, inputs, table rows; `--outline-strong (#d1d5db)` on form/ghost-button borders and on hover. **Left-accent borders** are a recurring motif used *purposefully*: nav items show a colored left border when active (`#7da9ff`), the part-notice card has a 4px primary left border, issue boxes a 3px amber left border, threaded replies a 2px indent line. Stat cards use a **3px colored top border** to signal state (blue/green/orange/yellow).

**Elevation (shadows).** A 4-step shadow scale (`--shadow-l1`…`l4`), all soft, low-spread, near-black at 4–14% opacity. Cards rest at **L1**; hover lifts objective cards to **L2** with a `translateY(-1px)`; modals sit at **L4**. The top bar carries a faint L1. No colored or glowing shadows except the logo badge's blue drop-shadow.

**Cards.** White surface, `--radius-md (8px)`, `--shadow-l1`, `1px --outline` border, `overflow:hidden`. Optional `card-header` (16/24px padding, bottom hairline) + `card-body` (24px padding). Stat cards center their content with a colored top accent.

**Buttons.** Compact, `--radius-sm`, 14px/500, `inline-flex` with `gap` for leading icon. Variants: `primary` (solid blue → navy on hover), `success`, `danger`, `ghost` (white, gray border, subtle gray fill on hover). Sizes `sm`/`xs` (xs has a 48px min-width, micro 12px). Disabled = 0.45 opacity. There's also a quiet `btn-add-action` (outlined, turns blue on hover) for "+ 등록" actions.

**Forms.** `form-control` = full-width, 1px `--outline-strong`, `--radius-sm`, 14px. Focus = primary border **+ 3px primary-tinted ring** (`0 0 0 3px rgba(primary,.12)`). An "inline" variant is borderless until hover/focus for in-place editing. Labels are 12px/600 uppercase secondary text. Custom 36×20 **toggle switch** with a sliding white knob.

**Badges & pills.** The workhorse element. Fully-round, 11px/600, tiny vertical padding. Soft-fill + matching text color per semantic: blue, green, red, yellow, orange, gray, purple (purple = a person/"questioner"). Count badges ("3건") and week chips ("W21") use gray/blue pills.

**Motion.** Restrained and fast. Transitions are **0.12–0.2s** on color/background/border/transform; bars/fills ease over **0.3–0.5s**. Named keyframes: `slideUp` (toast), `spin` (loader), `modal-in`/`tooltip-in` (8px rise + fade, 0.1–0.15s), and `focusPulse` (1.8s ring pulse to highlight a deep-linked item). **No bounces, no infinite decorative loops.** Respect reduced-motion in new work.

**Hover / press states.** Hover = subtle background tint (`--gray-50`/`--gray-100` or `--primary-light`), a darker border, or for the primary button a shift to navy. Table rows tint to `rgba(primary,.05)` and show a pointer. Active nav gains a tinted fill + colored left border + bolder weight. There's **no explicit shrink/scale-down press state**; the only transform is the objective card's hover lift. Comment action buttons fade in (`opacity 0→1`) on row hover.

**Transparency & blur.** Used lightly: modal scrim is `rgba(0,0,0,.45)` and the standard modal overlay adds `backdrop-filter: blur(2px)`; the lightbox overlay is `rgba(0,0,0,.85)`. Sidebar nav uses white-at-low-alpha layers for hover/active over the navy.

**Imagery vibe.** None native to the brand — the only user imagery is uploaded screenshots inside rich-text (Tiptap), shown at `max-width:100%`, `border-radius:4px`, openable in a dark lightbox. There are no brand photos or illustrations.

---

## 4. Iconography

**Primary system: Material Symbols Outlined** (Google Fonts, loaded via CDN). This is the single icon source across the app — there is **no custom icon font, sprite, or SVG icon set** in the repo.

- Loaded with the full variable axis: `opsz 20..48, wght 100..700, FILL 0..1, GRAD -50..200`.
- Default rendering: `font-size: 20px`, `font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24` — i.e. **outlined (unfilled), regular weight**.
- **Filled variants** (`'FILL' 1`) are used for emphasis: stat-card icons and the weekly-matrix link/warning icons.
- Sizes are contextual: 13–14px in matrix cells & meta rows, 16–18px in nav/buttons, 20px default, 28px stat icons, 40px empty-state icons.

**Icons in active use** (Material Symbols names): `dashboard`, `assignment`, `settings`, `feedback`, `help`, `logout`, `refresh`, `quiz`, `warning`, `link`, `campaign`, `forum`, `construction`, `arrow_forward`, `expand_more`, `add`, `close`, `chat_bubble_outline`, `search`.

**The one true brand mark: a bullseye / target** (concentric circles) — symbolizing OKR goals. It is a hand-authored inline SVG (not Material Symbols), rendered `currentColor` so it adapts: white inside the sidebar's blue gradient `logo-badge`, primary-blue on the login card. Stored here as [`assets/logo-mark.svg`](assets/logo-mark.svg).

**Emoji as icon?** No. Emoji appears only as affirmation text (👍) and the browser-tab favicon (📊) — never as functional UI iconography.

**Avatars** are initials, not images: a circle filled with `--primary-light`/`--primary` (member tables) or the `#2563eb→#7c3aed` gradient (top-bar user), showing the first character of the name.

**Guidance for new work:** use Material Symbols Outlined from the CDN; default to outlined/regular and only fill for emphasis. Reuse the bullseye mark for branding moments. Don't introduce a second icon family or hand-draw icons.

---

## 5. Index / Manifest

Root files:
- **`README.md`** — this document.
- **`colors_and_type.css`** — all design tokens (color, type, spacing, radius, shadow, layout) as CSS variables + ready-to-use semantic type classes. Import this first in any new file.
- **`SKILL.md`** — Agent-Skill manifest so this system works as a downloadable Claude Code skill.
- **`assets/`** — brand assets. `logo-mark.svg` (the bullseye/target mark, `currentColor`).
- **`preview/`** — design-system specimen cards (rendered in the Design System tab).
- **`ui_kits/work-management/`** — high-fidelity interactive recreation of the app. Start at `ui_kits/work-management/index.html`; components live alongside as `.jsx`. See its own `README.md`.

_No slide template was provided, so no `slides/` were generated._

---

## 6. Notes & Substitutions
- **Pretendard** is the product's intended typeface but is **not bundled** in the repo. We load it from its official jsDelivr CDN. If you have licensed/self-hosted Pretendard `woff2` files, drop them in `fonts/` and swap the `@import`.
- **Material Symbols** load from Google Fonts CDN exactly as the product does.
