from upbit_dashboard.upbit.runner import next_backoff


def test_next_backoff_doubles_until_maximum() -> None:
    assert next_backoff(current=1.0, maximum=30.0) == 2.0
    assert next_backoff(current=16.0, maximum=30.0) == 30.0
    assert next_backoff(current=30.0, maximum=30.0) == 30.0


def test_next_backoff_rejects_non_positive_values() -> None:
    try:
        next_backoff(current=0.0, maximum=30.0)
    except ValueError as exc:
        assert "current" in str(exc)
    else:
        raise AssertionError("next_backoff must reject non-positive current values")

    try:
        next_backoff(current=1.0, maximum=0.0)
    except ValueError as exc:
        assert "maximum" in str(exc)
    else:
        raise AssertionError("next_backoff must reject non-positive maximum values")

