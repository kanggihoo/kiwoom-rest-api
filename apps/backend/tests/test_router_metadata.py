from upbit_dashboard.main import create_app


def test_api_routes_have_domain_tags(monkeypatch) -> None:
    monkeypatch.setenv("UPBIT_WS_ENABLED", "false")
    schema = create_app().openapi()

    assert schema["paths"]["/api/markets"]["get"]["tags"] == ["markets"]
    assert schema["paths"]["/api/snapshot"]["get"]["tags"] == ["snapshot"]
    assert schema["paths"]["/api/candles"]["get"]["tags"] == ["candles"]
    assert schema["paths"]["/health"]["get"]["tags"] == ["health"]
