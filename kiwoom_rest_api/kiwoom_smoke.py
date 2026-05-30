from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv


REAL_BASE_URL = "https://api.kiwoom.com"
MOCK_BASE_URL = "https://mockapi.kiwoom.com"
DEFAULT_STOCK_CODE = "005930"


@dataclass(frozen=True)
class KiwoomConfig:
    app_key: str
    app_secret_key: str
    base_url: str = REAL_BASE_URL
    stock_code: str = DEFAULT_STOCK_CODE
    timeout_seconds: float = 10.0


def mask_secret(value: str | None) -> str:
    if not value or len(value) < 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def parse_price(value: str | None) -> int | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    return int(normalized.lstrip("+-").replace(",", ""))


def load_config(
    *,
    stock_code: str | None = None,
    base_url: str | None = None,
    use_mock: bool = False,
    timeout_seconds: float = 10.0,
) -> KiwoomConfig:
    load_dotenv()

    app_key = os.getenv("KIWOOM_APP_KEY", "").strip()
    app_secret_key = os.getenv("KIWOOM_APP_SECRET_KEY", "").strip()
    if not app_key or not app_secret_key:
        raise RuntimeError(
            ".env에 KIWOOM_APP_KEY와 KIWOOM_APP_SECRET_KEY가 모두 필요합니다."
        )

    resolved_base_url = (
        base_url
        or os.getenv("KIWOOM_BASE_URL", "").strip()
        or (MOCK_BASE_URL if use_mock else REAL_BASE_URL)
    )
    resolved_stock_code = (
        stock_code or os.getenv("KIWOOM_STOCK_CODE", "").strip() or DEFAULT_STOCK_CODE
    )

    return KiwoomConfig(
        app_key=app_key,
        app_secret_key=app_secret_key,
        base_url=resolved_base_url.rstrip("/"),
        stock_code=resolved_stock_code,
        timeout_seconds=timeout_seconds,
    )


def request_access_token(client: httpx.Client, config: KiwoomConfig) -> dict[str, Any]:
    response = client.post(
        f"{config.base_url}/oauth2/token",
        headers={
            "api-id": "au10001",
            "content-type": "application/json;charset=UTF-8",
        },
        json={
            "grant_type": "client_credentials",
            "appkey": config.app_key,
            "secretkey": config.app_secret_key,
        },
    )
    response.raise_for_status()

    payload = response.json()
    token = payload.get("token")
    if not token:
        raise RuntimeError(f"토큰 발급 응답에 token이 없습니다: {payload}")

    return payload


def build_stock_info_request(
    config: KiwoomConfig, token: str
) -> tuple[str, dict[str, str], dict[str, str]]:
    return (
        f"{config.base_url}/api/dostk/stkinfo",
        {
            "api-id": "ka10095",
            "authorization": f"Bearer {token}",
            "content-type": "application/json;charset=UTF-8",
        },
        {"stk_cd": config.stock_code},
    )


def request_stock_info(
    client: httpx.Client, config: KiwoomConfig, token: str
) -> dict[str, Any]:
    url, headers, body = build_stock_info_request(config, token)
    response = client.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()


def print_smoke_result(
    config: KiwoomConfig,
    token_payload: dict[str, Any],
    stock_payload: dict[str, Any],
) -> None:
    print("Kiwoom REST API smoke test")
    print(f"- base_url: {config.base_url}")
    print(f"- stock_code: {config.stock_code}")
    print(f"- token_type: {token_payload.get('token_type')}")
    print(f"- expires_dt: {token_payload.get('expires_dt')}")

    items = stock_payload.get("atn_stk_infr") or []
    if not items:
        print(f"- stock_return_code: {stock_payload.get('return_code')}")
        print(f"- stock_return_msg: {stock_payload.get('return_msg')}")
        print("- stock: no atn_stk_infr rows")
        return

    first = items[0]
    current_price = parse_price(first.get("cur_prc"))
    print("- stock:")
    print(f"  code: {first.get('stk_cd')}")
    print(f"  name: {first.get('stk_nm')}")
    print(f"  current_price: {current_price}")
    print(f"  raw_current_price: {first.get('cur_prc')}")
    print(f"  fluctuation_rate: {first.get('flu_rt')}")
    print(f"  trade_quantity: {first.get('trde_qty')}")
    print(f"  conclusion_time: {first.get('cntr_tm')}")


def run_smoke_test(config: KiwoomConfig) -> None:
    with httpx.Client(timeout=config.timeout_seconds) as client:
        token_payload = request_access_token(client, config)
        stock_payload = request_stock_info(client, config, token_payload["token"])

    print_smoke_result(config, token_payload, stock_payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Issue a Kiwoom token and query ka10095 stock info once."
    )
    parser.add_argument(
        "--stock-code",
        default=None,
        help=f"Stock code to query. Defaults to KIWOOM_STOCK_CODE or {DEFAULT_STOCK_CODE}.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use https://mockapi.kiwoom.com unless KIWOOM_BASE_URL is set.",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        help="Override Kiwoom base URL.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP timeout seconds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(
        stock_code=args.stock_code,
        base_url=args.base_url,
        use_mock=args.mock,
        timeout_seconds=args.timeout,
    )
    run_smoke_test(config)


if __name__ == "__main__":
    main()
