# Domain Docs

This repo uses a single-context domain documentation layout.

## Read before domain-sensitive work

- `CONTEXT.md` at the repo root.
- Relevant ADRs under `docs/adr/`.
- Upbit-specific planning docs under `docs/upbit/` when working on the dashboard.

If `CONTEXT.md` or a relevant ADR is missing detail, proceed from the existing docs and note the gap. Do not invent new domain vocabulary when the glossary already defines a term.

## Layout

```text
/
├── CONTEXT.md
├── docs/
│   ├── adr/
│   └── upbit/
└── apps/
    ├── web/
    └── backend/
```

## Vocabulary rule

Use the terms in `CONTEXT.md` for issue titles, plans, refactor proposals, test names, and architecture notes. If a new term is needed, add it to `CONTEXT.md` or call out that the glossary needs an update.

## ADR rule

If a proposed change conflicts with an ADR, call out the conflict explicitly before implementing.
