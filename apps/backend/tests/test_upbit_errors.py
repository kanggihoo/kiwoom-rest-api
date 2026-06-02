from upbit_dashboard.api.upbit_errors import map_upbit_rest_error
from upbit_dashboard.upbit.rest import UpbitRestError


def test_map_upbit_rest_error_maps_rate_limit_status() -> None:
    api_error = map_upbit_rest_error(
        UpbitRestError(
            status_code=429,
            message="Too many requests",
            error_name="429",
            remaining_req="group=candle; min=1800; sec=0",
        )
    )

    assert api_error.code == "RATE_LIMITED"
    assert api_error.status_code == 429
    assert api_error.details == {
        "upbitStatus": 429,
        "upbitErrorName": "429",
        "remainingReq": "group=candle; min=1800; sec=0",
    }
