#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "pypdf is required. Install it with `python3 -m pip install pypdf`."
    ) from exc


DEFAULT_PDF = "키움 REST API 문서.pdf"
TOTAL_TOC_PAGES = 6
FIELD_TYPES = {
    "String",
    "Integer",
    "Long",
    "Double",
    "Float",
    "Number",
    "Boolean",
    "LIST",
    "List",
    "Object",
    "Array",
}

CATEGORY_SLUGS = {
    "계좌": "account",
    "종목정보": "stock-info",
    "시세": "quote",
    "순위정보": "ranking",
    "차트": "chart",
    "실시간시세": "realtime",
    "ELW": "elw",
    "ETF": "etf",
    "주문": "order",
    "업종": "sector",
    "기관/외국인": "institution-foreign",
    "대차거래": "stock-loan",
    "조건검색": "condition-search",
    "신용주문": "margin-order",
    "테마": "theme",
    "공매도": "short-selling",
    "접근토큰발급": "token-issue",
    "접근토큰폐기": "token-revoke",
}


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def markdown_escape(value: Any) -> str:
    text = "" if value is None else str(value)
    text = text.replace("|", "\\|")
    text = text.replace("\n", "<br>")
    return text


def strip_page_noise(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d+\s*/\s*\d+", line):
            continue
        lines.append(line)
    return lines


def parse_toc_line(line: str) -> dict[str, Any] | None:
    tokens = line.split()
    if len(tokens) < 3 or not tokens[0].isdigit():
        return None

    no = int(tokens[0])
    if not tokens[-1].isdigit():
        return None
    start_page = int(tokens[-1])

    if tokens[1:3] == ["공통", "오류코드"]:
        return {
            "kind": "error_codes",
            "no": no,
            "api_id": None,
            "api_name": "공통 오류코드",
            "major_category": "공통",
            "middle_category": "오류코드",
            "start_page": start_page,
        }

    api_id = tokens[1]
    body = tokens[2:-1]

    if "국내주식" in body:
        major_index = body.index("국내주식")
        api_name = " ".join(body[:major_index])
        major_category = "국내주식"
        middle_category = body[major_index + 1]
    elif "OAuth" in body:
        major_index = body.index("OAuth")
        api_name = " ".join(body[:major_index])
        if major_index + 1 < len(body) and body[major_index + 1] == "인증":
            major_category = "OAuth 인증"
            middle_category = body[major_index + 2]
        else:
            major_category = "OAuth"
            middle_category = body[major_index + 1]
    else:
        raise ValueError(f"Unable to parse TOC row: {line}")

    return {
        "kind": "api",
        "no": no,
        "api_id": api_id,
        "api_name": api_name,
        "major_category": major_category,
        "middle_category": middle_category,
        "start_page": start_page,
    }


def parse_toc(reader: PdfReader) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for page_index in range(TOTAL_TOC_PAGES):
        text = reader.pages[page_index].extract_text() or ""
        for line in strip_page_noise(text):
            entry = parse_toc_line(line)
            if entry:
                entries.append(entry)

    entries.sort(key=lambda item: item["start_page"])
    for index, entry in enumerate(entries):
        if index + 1 < len(entries):
            entry["end_page"] = entries[index + 1]["start_page"] - 1
        else:
            entry["end_page"] = len(reader.pages)
    return entries


def page_range_lines(reader: PdfReader, start_page: int, end_page: int) -> list[str]:
    lines: list[str] = []
    for page_number in range(start_page, end_page + 1):
        text = reader.pages[page_number - 1].extract_text() or ""
        lines.extend(strip_page_noise(text))
    return lines


def line_value(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def collect_between(
    lines: list[str], start_marker: str, end_markers: tuple[str, ...]
) -> list[str]:
    collecting = False
    collected: list[str] = []
    for line in lines:
        if not collecting and line == start_marker:
            collecting = True
            continue
        if collecting and line in end_markers:
            break
        if collecting:
            collected.append(line)
    return collected


def parse_field_line(line: str) -> dict[str, str] | None:
    if not line.startswith(("Header ", "Body ")):
        return None

    tokens = line.split()
    if len(tokens) < 3:
        return None

    location = tokens[0]
    cursor = 1
    depth = 0
    while cursor < len(tokens) and tokens[cursor] == "-":
        depth += 1
        cursor += 1
    if cursor >= len(tokens):
        return None
    element = f"{'- ' * depth}{tokens[cursor]}".strip()
    cursor += 1

    type_index = -1
    for index in range(cursor, len(tokens)):
        if tokens[index] in FIELD_TYPES:
            type_index = index
            break

    if type_index == -1:
        return None

    korean_name = " ".join(tokens[cursor:type_index])
    field_type = tokens[type_index]
    cursor = type_index + 1

    required = ""
    if cursor < len(tokens) and tokens[cursor] in {"Y", "N"}:
        required = tokens[cursor]
        cursor += 1

    length = ""
    if cursor < len(tokens) and re.fullmatch(r"\d+", tokens[cursor]):
        length = tokens[cursor]
        cursor += 1

    description = " ".join(tokens[cursor:])
    return {
        "location": location,
        "element": element,
        "korean_name": korean_name,
        "type": field_type,
        "required": required,
        "length": length,
        "description": description,
    }


def parse_fields(section_lines: list[str]) -> list[dict[str, str]]:
    fields: list[dict[str, str]] = []
    ignored_prefixes = (
        "구분 ",
        "d Length Description",
        "API 정보",
        "기본정보",
        "키움 REST API",
    )
    ignored_exact = {"Request", "Response", "Request Example", "Response Example"}

    for line in section_lines:
        if line in ignored_exact or line.startswith(ignored_prefixes):
            continue
        row = parse_field_line(line)
        if row:
            fields.append(row)
            continue
        if fields and line:
            previous = fields[-1]["description"]
            fields[-1]["description"] = f"{previous}\n{line}" if previous else line
    return fields


def extract_example(lines: list[str], marker: str, stop_marker: str | None = None) -> str:
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line == marker:
            collecting = True
            continue
        if collecting and stop_marker and line == stop_marker:
            break
        if collecting:
            if line in {"Request Example", "Response Example"}:
                continue
            collected.append(line)
    return "\n".join(collected).strip()


def parse_api_detail(reader: PdfReader, entry: dict[str, Any]) -> dict[str, Any]:
    lines = page_range_lines(reader, entry["start_page"], entry["end_page"])
    request_lines = collect_between(lines, "Request", ("Response",))
    response_lines = collect_between(lines, "Response", ("Request Example",))
    overview = "\n".join(collect_between(lines, "개요", ("Request",))).strip()

    detail = {
        "menu_location": line_value(lines, "메뉴 위치"),
        "document_api_name": line_value(lines, "API 명"),
        "document_api_id": line_value(lines, "API ID"),
        "method": line_value(lines, "Method"),
        "production_domain": line_value(lines, "운영 도메인"),
        "mock_domain": line_value(lines, "모의투자 도메인"),
        "url": line_value(lines, "URL"),
        "format": line_value(lines, "Format"),
        "content_type": line_value(lines, "Content-Type"),
        "overview": overview,
        "request_fields": parse_fields(request_lines),
        "response_fields": parse_fields(response_lines),
        "request_example": extract_example(lines, "Request Example", "Response Example"),
        "response_example": extract_example(lines, "Response Example"),
    }
    return detail


def parse_error_codes(reader: PdfReader, entry: dict[str, Any]) -> list[dict[str, Any]]:
    lines = page_range_lines(reader, entry["start_page"], entry["end_page"])
    codes: list[dict[str, Any]] = []
    for line in lines:
        match = re.match(r"^(\d+)\s+(\d+)\s+(.+)$", line)
        if not match:
            continue
        codes.append(
            {
                "no": int(match.group(1)),
                "code": match.group(2),
                "message": match.group(3).strip(),
            }
        )
    return codes


def enrich_entries(reader: PdfReader, entries: list[dict[str, Any]]) -> dict[str, Any]:
    api_entries: list[dict[str, Any]] = []
    error_entry: dict[str, Any] | None = None
    error_codes: list[dict[str, Any]] = []

    for entry in entries:
        if entry["kind"] == "api":
            detail = parse_api_detail(reader, entry)
            api_entries.append({**entry, **detail})
        elif entry["kind"] == "error_codes":
            error_entry = entry
            error_codes = parse_error_codes(reader, entry)

    return {
        "source": DEFAULT_PDF,
        "generated_on": date.today().isoformat(),
        "total_pages": len(reader.pages),
        "api_count": len(api_entries),
        "error_code_count": len(error_codes),
        "apis": api_entries,
        "error_codes": {
            "entry": error_entry,
            "items": error_codes,
        },
    }


def api_doc_filename(api: dict[str, Any]) -> str:
    return f"{api['no']:03d}-{api['api_id']}.md"


def category_slug(category: str) -> str:
    if category in CATEGORY_SLUGS:
        return CATEGORY_SLUGS[category]
    slug = re.sub(r"[^0-9A-Za-z가-힣]+", "-", category).strip("-")
    return slug or "uncategorized"


def make_table(headers: list[str], rows: list[list[Any]]) -> str:
    output = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        output.append("| " + " | ".join(markdown_escape(value) for value in row) + " |")
    return "\n".join(output)


def field_table(fields: list[dict[str, str]]) -> str:
    if not fields:
        return "_문서에서 필드 표를 추출하지 못했습니다._"
    return make_table(
        ["위치", "Element", "한글명", "Type", "Required", "Length", "Description"],
        [
            [
                field["location"],
                field["element"],
                field["korean_name"],
                field["type"],
                field["required"],
                field["length"],
                field["description"],
            ]
            for field in fields
        ],
    )


def fenced_block(value: str, language: str = "json") -> str:
    if not value:
        return "_문서에 예시가 없습니다._"
    return f"```{language}\n{value}\n```"


def write_api_doc(api: dict[str, Any], path: Path) -> None:
    overview = api.get("overview") or "_문서에 별도 개요가 없습니다._"
    content = f"""# {api['api_id']} {api['api_name']}

- 분류: {api['major_category']} / {api['middle_category']}
- 메뉴 위치: {api.get('menu_location') or '-'}
- Method: `{api.get('method') or '-'}`
- 운영 도메인: `{api.get('production_domain') or '-'}`
- 모의투자 도메인: `{api.get('mock_domain') or '-'}`
- URL: `{api.get('url') or '-'}`
- Format: `{api.get('format') or '-'}`
- Content-Type: `{api.get('content_type') or '-'}`
- PDF 페이지: {api['start_page']}~{api['end_page']}

## 개요

{overview}

## Request Fields

{field_table(api.get('request_fields', []))}

## Response Fields

{field_table(api.get('response_fields', []))}

## Request Example

{fenced_block(api.get('request_example', ''), 'json')}

## Response Example

{fenced_block(api.get('response_example', ''), 'json')}
"""
    path.write_text(content, encoding="utf-8")


def write_overview(catalog: dict[str, Any], output_dir: Path) -> None:
    apis = catalog["apis"]
    by_middle = Counter(api["middle_category"] for api in apis)
    by_major = Counter(api["major_category"] for api in apis)

    major_rows = [[category, count] for category, count in by_major.most_common()]
    middle_rows = [[category, count] for category, count in by_middle.most_common()]

    content = f"""# Kiwoom REST API 문서 정리

이 디렉터리는 공식 PDF를 구조화해서 만든 작업용 문서입니다.

- 원본 PDF: `{catalog['source']}`
- 전체 페이지: {catalog['total_pages']}
- API 수: {catalog['api_count']}
- 공통 오류코드 수: {catalog['error_code_count']}
- 생성일: {catalog['generated_on']}

## 구성

- `api-index.md`: 전체 API 목차와 각 API 문서 링크
- `common.md`: 도메인, 인증, 공통 헤더, 연속조회 규칙
- `error-codes.md`: 공통 오류코드
- `categories/`: 중분류별 API 목록
- `apis/`: API ID별 상세 문서
- `../../data/kiwoom-api-catalog.json`: 코드에서 쓰기 쉬운 구조화 데이터

## 대분류 통계

{make_table(['대분류', 'API 수'], major_rows)}

## 중분류 통계

{make_table(['중분류', 'API 수'], middle_rows)}

## 재생성

```bash
python3 scripts/extract_kiwoom_rest_api_docs.py
```

PDF 표 추출 특성상 줄바꿈이 원문과 다를 수 있습니다. 주문, 계좌, 실시간시세처럼 실제 거래에 영향을 주는 API는 원문 PDF와 대조해서 최종 확인해야 합니다.
"""
    (output_dir / "overview.md").write_text(content, encoding="utf-8")


def write_common_doc(catalog: dict[str, Any], output_dir: Path) -> None:
    apis = catalog["apis"]
    rest_domains = sorted(
        {
            api["production_domain"]
            for api in apis
            if api.get("production_domain", "").startswith("https://")
        }
    )
    websocket_domains = sorted(
        {
            api["production_domain"]
            for api in apis
            if api.get("production_domain", "").startswith("wss://")
        }
    )
    mock_domains = sorted({api.get("mock_domain", "") for api in apis if api.get("mock_domain")})

    content = f"""# 공통 규칙

## 도메인

### REST

{make_table(['구분', '도메인'], [['운영', value] for value in rest_domains])}

### WebSocket

{make_table(['구분', '도메인'], [['운영', value] for value in websocket_domains])}

### 모의투자

{make_table(['도메인'], [[value] for value in mock_domains])}

## 인증 흐름

1. `au10001` 접근토큰 발급 API로 `appkey`, `secretkey`를 전달해 접근토큰을 발급합니다.
2. 이후 API 호출 시 Header `authorization`에 `Bearer <token>` 형식으로 접근토큰을 전달합니다.
3. 필요 시 `au10002` 접근토큰폐기 API로 토큰을 폐기합니다.

## 공통 Header

{make_table(
    ['Header', '필수', '설명'],
    [
        ['api-id', 'Y', '호출할 API ID 또는 실시간 항목 ID'],
        ['authorization', 'Y', 'Bearer 접근토큰'],
        ['cont-yn', 'N', '응답 Header의 연속조회여부가 Y인 경우 다음 조회 요청에 사용'],
        ['next-key', 'N', '응답 Header의 연속조회키가 있는 경우 다음 조회 요청에 사용'],
    ],
)}

## 연속조회

응답 Header의 `cont-yn` 값이 `Y`이면 다음 데이터가 있다는 뜻입니다. 다음 요청 Header에 응답으로 받은 `cont-yn`, `next-key` 값을 넣어 이어서 조회합니다.

## 응답 공통값

대부분의 예시 응답은 Body에 `return_code`, `return_msg`를 포함합니다. 오류 상세는 [error-codes.md](error-codes.md)를 기준으로 확인합니다.
"""
    (output_dir / "common.md").write_text(content, encoding="utf-8")


def write_api_index(catalog: dict[str, Any], output_dir: Path) -> None:
    apis = catalog["apis"]
    rows = []
    for api in apis:
        link = f"[{api['api_id']}](apis/{api_doc_filename(api)})"
        rows.append(
            [
                api["no"],
                link,
                api["api_name"],
                api["major_category"],
                api["middle_category"],
                f"{api['start_page']}~{api['end_page']}",
                api.get("method", ""),
                api.get("url", ""),
            ]
        )

    content = f"""# API Index

전체 API {len(apis)}개를 PDF 목차 순서대로 정리했습니다.

{make_table(['No', 'API ID', 'API 명', '대분류', '중분류', '페이지', 'Method', 'URL'], rows)}
"""
    (output_dir / "api-index.md").write_text(content, encoding="utf-8")


def write_category_docs(catalog: dict[str, Any], output_dir: Path) -> None:
    categories_dir = output_dir / "categories"
    categories_dir.mkdir(parents=True, exist_ok=True)
    for stale_doc in categories_dir.glob("*.md"):
        stale_doc.unlink()
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for api in catalog["apis"]:
        grouped[api["middle_category"]].append(api)

    category_index_rows = []
    for category in sorted(grouped):
        apis = sorted(grouped[category], key=lambda item: item["no"])
        slug = category_slug(category)
        filename = f"{slug}.md"
        category_index_rows.append([f"[{category}]({filename})", len(apis)])
        rows = [
            [
                api["no"],
                f"[{api['api_id']}](../apis/{api_doc_filename(api)})",
                api["api_name"],
                f"{api['start_page']}~{api['end_page']}",
                api.get("method", ""),
                api.get("url", ""),
            ]
            for api in apis
        ]
        content = f"""# {category}

API {len(apis)}개입니다.

{make_table(['No', 'API ID', 'API 명', '페이지', 'Method', 'URL'], rows)}
"""
        (categories_dir / filename).write_text(content, encoding="utf-8")

    index = f"""# Category Index

{make_table(['중분류', 'API 수'], category_index_rows)}
"""
    (categories_dir / "README.md").write_text(index, encoding="utf-8")


def write_error_codes(catalog: dict[str, Any], output_dir: Path) -> None:
    rows = [
        [item["no"], item["code"], item["message"]]
        for item in catalog["error_codes"]["items"]
    ]
    entry = catalog["error_codes"]["entry"] or {}
    content = f"""# 공통 오류코드

- PDF 페이지: {entry.get('start_page', '-')}

{make_table(['No', '오류코드', '오류메시지'], rows)}
"""
    (output_dir / "error-codes.md").write_text(content, encoding="utf-8")


def write_outputs(catalog: dict[str, Any], data_dir: Path, docs_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    api_docs_dir = docs_dir / "apis"
    api_docs_dir.mkdir(parents=True, exist_ok=True)
    for stale_doc in api_docs_dir.glob("*.md"):
        stale_doc.unlink()

    (data_dir / "kiwoom-api-catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    write_overview(catalog, docs_dir)
    write_common_doc(catalog, docs_dir)
    write_api_index(catalog, docs_dir)
    write_category_docs(catalog, docs_dir)
    write_error_codes(catalog, docs_dir)

    for api in catalog["apis"]:
        write_api_doc(api, api_docs_dir / api_doc_filename(api))


def validate_catalog(catalog: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    apis = catalog["apis"]
    api_ids = [api["api_id"] for api in apis]
    if len(api_ids) != len(set(api_ids)):
        errors.append("duplicate API IDs exist")
    if catalog["api_count"] != 207:
        errors.append(f"expected 207 APIs, got {catalog['api_count']}")
    if catalog["error_code_count"] != 33:
        errors.append(f"expected 33 error codes, got {catalog['error_code_count']}")
    for api in apis:
        for required_key in ("method", "production_domain", "url", "format", "content_type"):
            if not api.get(required_key):
                errors.append(f"{api['api_id']} missing {required_key}")
    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Kiwoom REST API PDF into JSON and Markdown docs."
    )
    parser.add_argument("--pdf", default=DEFAULT_PDF, help="Path to the source PDF")
    parser.add_argument("--data-dir", default="data", help="Output data directory")
    parser.add_argument("--docs-dir", default="docs/kiwoom", help="Output docs directory")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        return 1

    reader = PdfReader(str(pdf_path))
    entries = parse_toc(reader)
    catalog = enrich_entries(reader, entries)
    catalog["source"] = str(pdf_path)

    errors = validate_catalog(catalog)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    write_outputs(catalog, Path(args.data_dir), Path(args.docs_dir))
    print(
        f"Generated {catalog['api_count']} API docs, "
        f"{catalog['error_code_count']} error codes, "
        f"and {len(Counter(api['middle_category'] for api in catalog['apis']))} category docs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
