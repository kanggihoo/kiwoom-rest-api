# Kiwoom REST API Docs

키움 REST API 공식 PDF를 구조화해서 Markdown 문서와 JSON 카탈로그로 정리한 저장소입니다.

원본 PDF는 공개 저장소에 포함하지 않습니다. 로컬에 PDF를 두고 추출 스크립트를 실행하면 문서를 다시 생성할 수 있습니다.

## 주요 문서

- [문서 개요](docs/kiwoom/overview.md)
- [API 인덱스](docs/kiwoom/api-index.md)
- [공통 규칙](docs/kiwoom/common.md)
- [공통 오류코드](docs/kiwoom/error-codes.md)
- [종목 가격 알림 서비스용 API 읽기 가이드](docs/kiwoom/price-alert-service-guide.md)

## 데이터

- [구조화 JSON 카탈로그](data/kiwoom-api-catalog.json)

## 간단 API 테스트

프로젝트 루트의 `.env`에 `KIWOOM_APP_KEY`, `KIWOOM_APP_SECRET_KEY`를 둔 뒤 실행합니다.

```bash
uv run python -m kiwoom_rest_api.kiwoom_smoke --stock-code 005930
```

기본값은 운영 도메인(`https://api.kiwoom.com`)입니다. 모의투자 도메인을 쓰려면 `--mock`을 붙입니다.

## 재생성

프로젝트 루트에 원본 PDF를 둔 뒤 실행합니다.

```bash
python3 -m pip install -r requirements.txt
python3 scripts/extract_kiwoom_rest_api_docs.py
```

기본 PDF 파일명은 `키움 REST API 문서.pdf`입니다. 다른 파일명을 쓰려면 `--pdf` 옵션을 사용합니다.

```bash
python3 scripts/extract_kiwoom_rest_api_docs.py --pdf "Kiwoom REST API.pdf"
```

## 주의

PDF 표 추출 특성상 줄바꿈과 예시 JSON의 쉼표 누락 같은 원문 문제까지 그대로 반영될 수 있습니다. 주문, 계좌, 실시간시세처럼 실제 거래에 영향을 주는 API는 원문 PDF와 대조해 최종 확인해야 합니다.
