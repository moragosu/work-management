# work-management — UI Kit

A high-fidelity, interactive recreation of the **설비혁신파트 협업 시스템** (Facility-Innovation Part Collaboration System) web app — an internal OKR & weekly-progress tool. Built to match the shipped Vue app (`moragosu/work-management → frontend/`) using its real design tokens and component styles.

## Run it
Open `index.html`. You land on the **login** screen — credentials are pre-filled, just press **로그인**. From there the left nav switches between the recreated screens. Use the top-bar **logout** icon to return to login.

## Screens
| Screen | File | Notes |
|---|---|---|
| **Login** | `Login.jsx` | Branded auth card with the bullseye logo lockup |
| **대시보드 (Dashboard)** | `Dashboard.jsx` | KPI stat cards, part notice, two action panels (의견/질문 + 진행 현황/이슈) with week & status filters, per-member activity table with stat bars, weekly registration matrix, objective/KR cards, detail modal |
| **주간 진행 현황 (Progress)** | `Progress.jsx` | Week navigator, per-task cards with issue boxes, threaded comments/replies, and Q&A — add an issue or answer a question live |
| **관리 도구 (Admin)** | `Admin.jsx` | Tabbed tables for objectives·KR, tasks·sub-tasks, and staff; admin-mode toggle |
| **피드백 / 도움말** | `app.jsx` | Placeholders — these screens weren't recreated (flagged in-app) |

## Architecture
- **`index.html`** — loads React 18 + Babel, then the scripts below in order.
- **`kit.css`** — all component & layout styles (imports `../../colors_and_type.css` for tokens). Faithful to the product's `style.css` + `App.vue` shell.
- **`data.js`** — `window.KIT_DATA`: fake but realistic OKR-domain content (objectives, tasks, staff, issues, questions, confluence links).
- **`Primitives.jsx`** — `Icon, Badge, Button, AddButton, Card, Avatar, Toggle, FilterGroup, Modal, Toast` + `statusBadgeClass`, `formatWeekLabel`. All exported to `window`.
- **`Shell.jsx`** — `Sidebar`, `TopBar`, `LogoMark`.
- **`Login.jsx`, `Dashboard.jsx`, `Progress.jsx`, `Admin.jsx`** — the views.
- **`app.jsx`** — login gate + nav routing.

Components share scope by assigning to `window` at the end of each file (required for multi-file Babel).

## Fidelity notes
- Icons are **Material Symbols Outlined** (loaded via the token CSS). They render as real glyphs in a browser; static html-to-image screenshots show the ligature *name* instead — that's a capture limitation, not a bug.
- These are cosmetic recreations: state is local and resets on reload; there is no backend, auth, or persistence.
- The Tiptap rich-text editor is represented by plain `<textarea>` + rendered prose, not the real WYSIWYG.
