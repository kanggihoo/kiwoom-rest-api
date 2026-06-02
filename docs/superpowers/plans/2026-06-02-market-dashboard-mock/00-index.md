# Market Dashboard Mock Implementation Plan Index

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Execute the files below in numeric order.

**Goal:** Mock 데이터 기반 Upbit Market dashboard 1차 데스크톱 풀 레이아웃을 구현한다.

**Architecture:** 이 구현은 환경설정, mock 데이터, shell, chart, market panels, 검증을 단계별 plan으로 분리한다. 각 단계는 자체 커밋 단위를 가지며, FastAPI backend 없이 Next.js frontend와 local mock fixture만으로 실행 가능해야 한다.

**Tech Stack:** Next.js 16 App Router, React 19, Tailwind CSS v4, shadcn/ui, Pretendard local font, lucide-react, lightweight-charts, Vitest.

---

## Source Spec

- [Market Dashboard Mock 디자인 프로토타입 설계](../../specs/2026-06-02-market-dashboard-mock-design.md)

## Execution Order

| 순서 | Plan | 목적 | 완료 기준 |
| --- | --- | --- | --- |
| 1 | [01-setup.md](01-setup.md) | shadcn/ui, Pretendard, CSS token bridge, visual dependency 준비 | `components.json`, shadcn components, font, `globals.css` 연결 완료 |
| 2 | [02-data.md](02-data.md) | mock 데이터, view model 타입, formatter, 단위 테스트 준비 | mock fixture와 formatter tests 통과 |
| 3 | [03-shell.md](03-shell.md) | `page.tsx`, top navigation, index strip, desktop shell 작성 | dashboard shell이 mock data를 받아 렌더링 |
| 4 | [04-chart.md](04-chart.md) | Selected Market header와 Lightweight Charts mock chart 작성 | mock candle과 volume chart 렌더링 |
| 5 | [05-panels.md](05-panels.md) | 오른쪽 Market List, orderbook, trades, 하단 Market Table 작성 | 데스크톱 풀 레이아웃 완성 |
| 6 | [06-verification.md](06-verification.md) | lint/test/build, dev server, screenshot, visual checklist 검증 | blank chart, text overlap, 깨진 token 없음 |

## Execution Policy

- 각 plan 파일은 숫자 순서대로 실행한다.
- 각 stage의 커밋 단위를 유지한다.
- 이번 범위에서는 FastAPI backend를 실행하지 않는다.
- 이번 범위에서는 실제 REST/WebSocket 데이터를 연결하지 않는다.
- 이번 범위에서는 Zustand, TanStack Query, Zod, Storybook을 설치하지 않는다.
- 버튼, 탭, 검색, favorite은 시각 상태만 구현하고 실제 interaction은 구현하지 않는다.

## Final Verification

최종 완료 전 [06-verification.md](06-verification.md)를 반드시 실행한다.

필수 검증:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm lint
pnpm test
pnpm build
```

브라우저 검증:

```text
http://localhost:3000
1440x900
1728x1117
```
