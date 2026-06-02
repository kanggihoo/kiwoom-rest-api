# Market Dashboard Mock Stage 1 Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `apps/web`에 shadcn/ui, Pretendard, lucide-react, lightweight-charts, DESIGN.md CSS token bridge를 연결해 mock dashboard UI를 만들 수 있는 기반을 준비한다.

**Architecture:** 이 단계는 화면 컴포넌트를 만들지 않고 frontend 환경만 정리한다. `src/app/globals.css`를 실제 Tailwind v4 entrypoint로 고정하고, `design.tailwind.css`와 `design.shadcn.css`를 import해 shadcn semantic token이 DESIGN.md 색상/반경/폰트를 사용하도록 만든다.

**Tech Stack:** Next.js 16 App Router, React 19, Tailwind CSS v4, shadcn/ui radix base, Pretendard local font, lucide-react, lightweight-charts.

---

## 파일 구조

- Modify: `apps/web/package.json`
- Modify: `apps/web/pnpm-lock.yaml`
- Create: `apps/web/components.json`
- Create: `apps/web/src/lib/utils.ts`
- Create: `apps/web/src/app/fonts/PretendardVariable.woff2`
- Modify: `apps/web/src/app/layout.tsx`
- Modify: `apps/web/src/app/globals.css`
- Create via shadcn CLI: `apps/web/src/components/ui/*`

## Task 1: shadcn/ui 프로젝트 설정

**Files:**
- Create: `apps/web/components.json`
- Create: `apps/web/src/lib/utils.ts`
- Modify: `apps/web/package.json`
- Modify: `apps/web/pnpm-lock.yaml`

- [ ] **Step 1: 현재 shadcn 감지 상태 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dlx shadcn@latest info --json
```

Expected:

```text
"framework": "Next.js"
"tailwindVersion": "v4"
"rsc": true
"config": null
```

- [ ] **Step 2: shadcn/ui 초기화**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dlx shadcn@latest init --defaults
```

Expected:

```text
components.json created
src/lib/utils.ts created
```

- [ ] **Step 3: `components.json`을 dashboard 기준으로 고정**

Edit `apps/web/components.json` to this content:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "",
    "css": "src/app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "iconLibrary": "lucide"
}
```

- [ ] **Step 4: `cn()` utility 확인**

`apps/web/src/lib/utils.ts` must contain:

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

- [ ] **Step 5: shadcn info 재확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dlx shadcn@latest info --json
```

Expected:

```text
"tailwindCss": "src/app/globals.css"
"importAlias": "@"
"components" is an array
```

- [ ] **Step 6: 설정 변경 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/components.json apps/web/src/lib/utils.ts apps/web/package.json apps/web/pnpm-lock.yaml
git commit -m "chore(web): initialize shadcn ui"
```

Expected:

```text
[branch commit] chore(web): initialize shadcn ui
```

## Task 2: dashboard 1차 shadcn/ui 컴포넌트 추가

**Files:**
- Create: `apps/web/src/components/ui/button.tsx`
- Create: `apps/web/src/components/ui/card.tsx`
- Create: `apps/web/src/components/ui/badge.tsx`
- Create: `apps/web/src/components/ui/input.tsx`
- Create: `apps/web/src/components/ui/input-group.tsx`
- Create: `apps/web/src/components/ui/table.tsx`
- Create: `apps/web/src/components/ui/tabs.tsx`
- Create: `apps/web/src/components/ui/toggle-group.tsx`
- Create: `apps/web/src/components/ui/separator.tsx`
- Create: `apps/web/src/components/ui/scroll-area.tsx`
- Create: `apps/web/src/components/ui/skeleton.tsx`
- Create: `apps/web/src/components/ui/tooltip.tsx`
- Create: `apps/web/src/components/ui/dropdown-menu.tsx`
- Create: `apps/web/src/components/ui/select.tsx`
- Create: `apps/web/src/components/ui/switch.tsx`
- Modify: `apps/web/package.json`
- Modify: `apps/web/pnpm-lock.yaml`

- [ ] **Step 1: 사용할 컴포넌트 문서 URL 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dlx shadcn@latest docs button card badge input input-group table tabs toggle-group separator scroll-area skeleton tooltip dropdown-menu select switch
```

Expected:

```text
button
card
badge
input
input-group
table
tabs
toggle-group
separator
scroll-area
skeleton
tooltip
dropdown-menu
select
switch
```

- [ ] **Step 2: shadcn/ui 컴포넌트 추가**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm dlx shadcn@latest add button card badge input input-group table tabs toggle-group separator scroll-area skeleton tooltip dropdown-menu select switch
```

Expected:

```text
components/ui files created
```

- [ ] **Step 3: 생성 파일 import alias 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
rg '"@/lib/utils"|from "@/lib/utils"|from "@/components/ui' apps/web/src/components/ui apps/web/src/lib
```

Expected:

```text
apps/web/src/components/ui/button.tsx
apps/web/src/components/ui/card.tsx
apps/web/src/components/ui/input.tsx
```

- [ ] **Step 4: 컴포넌트 생성 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/components/ui apps/web/package.json apps/web/pnpm-lock.yaml
git commit -m "chore(web): add dashboard shadcn components"
```

Expected:

```text
[branch commit] chore(web): add dashboard shadcn components
```

## Task 3: chart와 icon 의존성 추가

**Files:**
- Modify: `apps/web/package.json`
- Modify: `apps/web/pnpm-lock.yaml`

- [ ] **Step 1: 필요한 runtime 의존성 추가**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm add lucide-react lightweight-charts
```

Expected:

```text
dependencies:
+ lucide-react
+ lightweight-charts
```

- [ ] **Step 2: 설치 결과 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm list lucide-react lightweight-charts --depth 0
```

Expected:

```text
lucide-react
lightweight-charts
```

- [ ] **Step 3: 의존성 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/package.json apps/web/pnpm-lock.yaml
git commit -m "chore(web): add dashboard visual dependencies"
```

Expected:

```text
[branch commit] chore(web): add dashboard visual dependencies
```

## Task 4: Pretendard font asset 추가

**Files:**
- Create: `apps/web/src/app/fonts/PretendardVariable.woff2`

- [ ] **Step 1: font 디렉터리 생성**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
mkdir -p src/app/fonts
```

Expected:

```text
src/app/fonts directory exists
```

- [ ] **Step 2: Pretendard variable woff2 다운로드**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
curl -L "https://unpkg.com/pretendard@1.3.9/dist/web/variable/woff2/PretendardVariable.woff2" -o src/app/fonts/PretendardVariable.woff2
```

Expected:

```text
PretendardVariable.woff2 downloaded
```

- [ ] **Step 3: font 파일 크기 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
ls -lh src/app/fonts/PretendardVariable.woff2
```

Expected:

```text
PretendardVariable.woff2 size is greater than 100K
```

- [ ] **Step 4: font asset 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/app/fonts/PretendardVariable.woff2
git commit -m "chore(web): add pretendard variable font"
```

Expected:

```text
[branch commit] chore(web): add pretendard variable font
```

## Task 5: Next layout과 global CSS token 연결

**Files:**
- Modify: `apps/web/src/app/layout.tsx`
- Modify: `apps/web/src/app/globals.css`

- [ ] **Step 1: `layout.tsx`에서 Pretendard 연결**

Replace `apps/web/src/app/layout.tsx` with:

```tsx
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const pretendard = localFont({
  src: "./fonts/PretendardVariable.woff2",
  variable: "--font-pretendard",
  weight: "100 900",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Upbit Dashboard",
  description: "Realtime Upbit monitoring dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${pretendard.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
```

- [ ] **Step 2: `globals.css`에서 디자인 token bridge 연결**

Replace `apps/web/src/app/globals.css` with:

```css
@import "tailwindcss";
@import "../../design.tailwind.css";
@import "../../design.shadcn.css";

@theme inline {
  --font-sans: var(--font-pretendard), Pretendard, Inter, "Apple SD Gothic Neo",
    system-ui, sans-serif;
}

html {
  min-height: 100%;
}

body {
  min-height: 100%;
  font-family: var(--font-pretendard), Pretendard, Inter, "Apple SD Gothic Neo",
    system-ui, sans-serif;
  font-feature-settings: "tnum";
}
```

- [ ] **Step 3: CSS import 경로 검증**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm build
```

Expected:

```text
Compiled successfully
```

- [ ] **Step 4: layout/CSS 커밋**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git add apps/web/src/app/layout.tsx apps/web/src/app/globals.css
git commit -m "chore(web): connect dashboard design tokens"
```

Expected:

```text
[branch commit] chore(web): connect dashboard design tokens
```

## Task 6: Stage 1 전체 검증

**Files:**
- Verify: `apps/web`

- [ ] **Step 1: lint 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm lint
```

Expected:

```text
No ESLint warnings or errors
```

- [ ] **Step 2: test 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm test
```

Expected:

```text
Test Files  pass
Tests  pass
```

- [ ] **Step 3: build 실행**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api/apps/web
pnpm build
```

Expected:

```text
Compiled successfully
```

- [ ] **Step 4: stage 완료 상태 확인**

Run:

```bash
cd /Users/kkh/Desktop/kiwoom-rest-api
git status --short
```

Expected:

```text
No Stage 1 files remain unstaged
```
