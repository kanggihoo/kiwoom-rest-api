# 프론트엔드 초기 설정 가이드

이 문서는 키움 REST API 대시보드용 프론트엔드 초기 설정 내용을 기록합니다.
프론트엔드 프로젝트는 에이전트가 자동 생성하지 않고, 개발자가 CLI 프롬프트를 직접 선택하면서 초기화하는 것을 기준으로 합니다.

## 목표

키움 API를 통해 가져온 데이터를 대시보드 형태로 시각화합니다.

초기 대시보드는 다음과 같은 화면 구성을 목표로 합니다.

- 주요 값과 상태를 보여주는 요약 카드
- 관심 종목 또는 검색 종목 화면
- TradingView Lightweight Charts 기반 가격 차트 패널
- 시세, 계좌, 주문성 데이터를 보여주는 테이블
- Storybook을 통한 UI 컴포넌트 문서화와 상태 예시 관리

## 권장 디렉터리

저장소 루트 아래에 독립적인 프론트엔드 디렉터리를 둡니다.

```powershell
C:\Users\SSAFY\Desktop\kiwoom-rest-api\frontend
```

이 구조는 기존 Python 패키지, 문서, 데이터 파일과 Next.js 앱 설정이 섞이지 않도록 해줍니다.

## 사용 스택

- 프레임워크: Next.js
- 패키지 매니저: pnpm
- 언어: TypeScript
- 스타일링: Tailwind CSS
- UI 컴포넌트: shadcn/ui
- 아이콘: lucide-react
- 차트: lightweight-charts
- 폰트: Pretendard
- 컴포넌트 문서화: Storybook

## 사전 확인

초기화 전에 로컬 런타임 버전을 확인합니다.

```powershell
node --version
pnpm --version
```

현재 Storybook 호환성을 기준으로 Node.js 20 이상, pnpm 9 이상을 사용하는 것이 좋습니다.

## Next.js 프로젝트 생성

저장소 루트에서 실행합니다.

```powershell
cd C:\Users\SSAFY\Desktop\kiwoom-rest-api
pnpm create next-app frontend --ts --tailwind --eslint --app --src-dir --import-alias "@/*" --use-pnpm
```

CLI가 대화형 질문을 표시하면 다음처럼 선택합니다.

```text
TypeScript: Yes
Linter: ESLint
Tailwind CSS: Yes
src/ directory: Yes
App Router: Yes
Import alias: @/*
Package manager: pnpm
```

권장 초기 구조는 다음과 같습니다.

```text
frontend/
  src/
    app/
    components/
      ui/
    features/
      dashboard/
      charts/
      symbols/
    lib/
    types/
```

## shadcn/ui 초기화

Next.js 프로젝트가 생성된 뒤 실행합니다.

```powershell
cd C:\Users\SSAFY\Desktop\kiwoom-rest-api\frontend
pnpm dlx shadcn@latest init
```

권장 선택값은 다음과 같습니다.

```text
Style: New York
Base color: Neutral 또는 Zinc
CSS variables: Yes
```

대시보드에 필요한 컴포넌트부터 작게 추가합니다.

```powershell
pnpm dlx shadcn@latest add button card badge table tabs input select skeleton separator dropdown-menu sheet
```

shadcn/ui 컴포넌트는 `src/components/ui`에 둡니다.
도메인 전용 컴포넌트는 `src/features/dashboard/components`처럼 별도 위치에 둡니다.

## 대시보드 라이브러리 설치

```powershell
pnpm add lightweight-charts lucide-react
```

주의사항:

- `lightweight-charts`는 브라우저 DOM이 필요하므로 client component에서만 사용합니다.
- `lucide-react`는 shadcn/ui와 커스텀 대시보드 버튼/도구 아이콘에 사용합니다.

## Pretendard 폰트 설정

Pretendard는 pnpm 패키지로 설치하지 않고 `.woff2` 파일을 프로젝트 안에서 직접 관리합니다.
Next.js에서는 `next/font/local`을 사용하면 로컬 폰트 파일을 빌드 시점에 최적화해서 사용할 수 있습니다.

권장 위치:

```text
frontend/
  src/
    app/
      fonts/
        PretendardVariable.woff2
```

`src/app/layout.tsx`에서 로컬 폰트를 등록합니다.

```tsx
import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const pretendard = localFont({
  src: "./fonts/PretendardVariable.woff2",
  variable: "--font-pretendard",
  display: "swap",
  weight: "45 920",
});

export const metadata: Metadata = {
  title: "Kiwoom Dashboard",
  description: "Kiwoom REST API dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className={`${pretendard.variable} antialiased`}>{children}</body>
    </html>
  );
}
```

`src/app/globals.css`에서는 CSS 변수로 기본 폰트를 연결합니다.

```css
@import "tailwindcss";

body {
  font-family:
    var(--font-pretendard),
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
}
```

Tailwind CSS v4를 사용한다면 `globals.css`에 다음처럼 `--font-sans`를 연결할 수도 있습니다.

```css
@theme inline {
  --font-sans: var(--font-pretendard);
}
```

이렇게 설정하면 Tailwind의 `font-sans` 유틸리티도 Pretendard를 사용합니다.

폰트 파일은 라이선스를 확인한 뒤 저장소에 포함합니다. Pretendard의 variable `.woff2` 파일 하나로 시작하고, 특정 굵기 파일을 나눠서 관리할 필요가 생기면 그때 regular, medium, semibold, bold 같은 개별 파일로 분리합니다.

## Lightweight Charts 사용 규칙

차트 컴포넌트는 client component로 분리합니다.

```tsx
"use client";

import { createChart } from "lightweight-charts";
import { useEffect, useRef } from "react";

export function PriceChart() {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      height: 320,
      layout: {
        background: { color: "transparent" },
        textColor: "#111827",
      },
    });

    return () => chart.remove();
  }, []);

  return <div ref={containerRef} className="h-80 w-full" />;
}
```

차트 생명주기 로직과 대시보드 레이아웃 로직이 섞이지 않도록 `PriceChartCard`, `VolumeChart`, `IntradayChart` 같은 래퍼 컴포넌트를 둡니다.

## Storybook 설정

Storybook은 UI 컴포넌트 문서화와 상태 예시 관리를 위해 사용합니다.
프로젝트 설명 문서는 `docs/`에 유지하고, Storybook은 재사용 가능한 React 컴포넌트와 화면 조각을 문서화하는 용도로 사용합니다.

`frontend/` 안에서 실행합니다.

```powershell
cd C:\Users\SSAFY\Desktop\kiwoom-rest-api\frontend
pnpm create storybook@latest
```

Next.js 프레임워크 선택지가 나오면 Vite 기반 Next.js Storybook 통합을 우선 선택합니다.

설정 후 예상되는 scripts는 다음과 같습니다.

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build"
  }
}
```

권장 story 위치:

```text
src/components/**/*.stories.tsx
src/features/**/*.stories.tsx
```

## 키움 API 경계

키움 app key, secret key, token, 계좌 식별 정보는 브라우저 코드에 노출하면 안 됩니다.

권장 데이터 흐름:

```text
브라우저 대시보드
  -> Next.js server route 또는 기존 Python 백엔드
  -> 키움 API 클라이언트
  -> 키움 REST API
```

`NEXT_PUBLIC_` 접두사가 붙은 프론트엔드 환경 변수는 브라우저에 노출됩니다.
키움 인증 정보에는 이 접두사를 사용하지 않습니다.

초기 연동 방식 후보:

- 기존 Python API/client를 백엔드 경계로 유지하고 Next.js가 해당 백엔드를 호출합니다.
- Next.js Route Handlers를 얇은 Backend-for-Frontend 계층으로 둡니다.
- Storybook과 대시보드 UI는 먼저 mock JSON fixture로 만들고, 이후 실제 API 데이터에 연결합니다.

현재 저장소 기준으로 가장 안전한 첫 단계는 다음 순서입니다.

1. `frontend/` 앱을 스캐폴딩합니다.
2. 키움 데이터 형태를 흉내 낸 mock 데이터로 대시보드 컴포넌트를 만듭니다.
3. Storybook에 컴포넌트 상태를 문서화합니다.
4. 대시보드 구조가 안정된 뒤 서버 측 데이터 경계를 추가합니다.

## 최초 확인 명령

초기화 후 Next.js 개발 서버를 실행합니다.

```powershell
cd C:\Users\SSAFY\Desktop\kiwoom-rest-api\frontend
pnpm dev
```

브라우저에서 확인합니다.

```text
http://localhost:3000
```

Storybook 실행:

```powershell
pnpm storybook
```

브라우저에서 확인합니다.

```text
http://localhost:6006
```

나중에 프론트엔드 변경사항을 커밋하기 전에는 다음 명령을 확인합니다.

```powershell
pnpm lint
pnpm build
pnpm build-storybook
```

## 참고 문서

- Next.js create-next-app CLI: https://nextjs.org/docs/app/api-reference/cli/create-next-app
- shadcn/ui Next.js 설치: https://ui.shadcn.com/docs/installation/next
- Storybook Next.js 프레임워크 문서: https://storybook.js.org/docs/get-started/frameworks/nextjs
- Lightweight Charts 시작 문서: https://tradingview.github.io/lightweight-charts/docs
- Next.js 폰트 최적화: https://nextjs.org/docs/app/getting-started/fonts
- lucide-react 패키지: https://www.npmjs.com/package/lucide-react
