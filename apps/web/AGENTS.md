<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Frontend Design Skills

Use the installed frontend skills when working on Next.js, React, shadcn/ui, Vercel deployment, frontend design, design systems, or DESIGN.md.

When designing or implementing frontend UI with Next.js, read `DESIGN.md` in this directory first and write code that follows its design system, visual rules, tokens, and component guidance.

- `vercel-react-best-practices`: React and Next.js performance, data fetching, bundle, and framework guidance.
- `vercel-composition-patterns`: scalable React composition patterns for reusable component APIs.
- `deploy-to-vercel`: Vercel deployment and preview deployment workflow.
- `shadcn`: official shadcn/ui component discovery, docs, add/update, presets, and project config workflow.
- `taste-skill` set: high-end visual design, frontend taste, redesign, image-to-code, and UI direction helpers.
- `frontend-design`: production-grade frontend interface design for websites, dashboards, app screens, and components.
- `web-artifacts-builder`: React/Tailwind web artifact building.
- `brand-guidelines`: brand color and typography application.
- `theme-factory`: font and color theme application.
- `web-design-guidelines`: Vercel web interface design guidelines.
- `design-md`: DESIGN.md creation and maintenance for design direction, tokens, and visual rules.

For shadcn/ui projects, inspect `components.json` and `globals.css` before generating or updating `DESIGN.md`. Prefer shadcn semantic tokens such as `bg-background`, `text-foreground`, `border-border`, `ring-ring`, `bg-primary`, and `text-primary-foreground` instead of raw Tailwind colors.

When creating or updating `DESIGN.md`, read `docs/spec.md` if it exists and ask whether to use the `@google/design.md` CLI workflow. If shadcn/ui compatibility is needed for a generated CSS file, also read `docs/shadcn-tailwind-v4.md` and `docs/shadcn-theming.md` if they exist. The generated DESIGN.md CSS should be bridged to shadcn/ui variables in `globals.css` using the Tailwind v4 `@theme inline` pattern, instead of replacing shadcn semantic variable names.

If the user agrees to the CLI workflow, validate changes with:

```bash
npx @google/design.md lint DESIGN.md
```

Use the CLI export command when the user wants DESIGN.md tokens converted into implementation assets:

```bash
npx @google/design.md export --format css-tailwind DESIGN.md > theme.css
npx @google/design.md export --format json-tailwind DESIGN.md > tailwind.theme.json
npx @google/design.md export --format dtcg DESIGN.md > tokens.json
```
