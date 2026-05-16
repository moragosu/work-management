# Agent Guide

## Project

This is the AX to-be frontend, built with SvelteKit 2, Svelte 4, TypeScript, Vite, and Tailwind CSS.

## Commands

- Install dependencies with `npm install` when needed.
- Run the dev server with `npm run dev -- --host 0.0.0.0 --port 5173`.
- Verify production builds with `npm run build`.

## UI Work

- Use the local AX skills in `.agents/skills/` for UI modernization and styling work.
- Start broad UI restyling with `ax-ui-design-system-orchestrator`, then apply the sibling skills it references.
- Preserve existing visible text, data meaning, route behavior, API payloads, and business logic unless the user explicitly asks for functional changes.
- Keep Svelte changes scoped to the relevant route, component, store, or utility.

## Design Assets

- SamsungOneKorean font assets live in `.agents/skills/ax-ui-visual-tokens/assets/fonts/`.
- When the app needs those fonts at runtime, copy the required weights into `static/fonts/` and define `@font-face` using `font-family: "SamsungOne"`.
- Main symbol SVG assets live in `.agents/skills/ax-ui-iconography/assets/`.

## Git Safety

- Do not revert user changes or unrelated work.
- Check `git status --short` before and after edits when making code or asset changes.
