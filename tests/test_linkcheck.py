from civic_atlas import linkcheck


def test_collect_urls_finds_sources_and_channels(fixture_catalog):
    urls = linkcheck.collect_urls(fixture_catalog)
    assert "https://example.org/springfield/request" in urls
    assert urls["https://example.org/springfield/request"] == {
        "report-missed-collection",
        "report-pothole",
    }
    assert "https://example.org/springfield/routing" in urls


def test_outcomes(monkeypatch):
    codes = {"https://ok.example": 200, "https://blocked.example": 403, "https://gone.example": 404}
    calls = []

    def fake_request(url, method, timeout):
        calls.append(method)
        return codes[url]

    monkeypatch.setattr(linkcheck, "_request", fake_request)
    assert linkcheck.check_url("https://ok.example")[0] == "ok"
    assert linkcheck.check_url("https://blocked.example")[0] == "unverifiable"
    assert linkcheck.check_url("https://gone.example")[0] == "broken"
    assert set(calls) == {"HEAD"}


def test_head_not_allowed_falls_back_to_get(monkeypatch):
    def fake_request(url, method, timeout):
        return 405 if method == "HEAD" else 200

    monkeypatch.setattr(linkcheck, "_request", fake_request)
    assert linkcheck.check_url("https://x.example") == ("ok", "200")


def test_user_agent_has_no_personal_contact():
    assert "@" not in linkcheck.USER_AGENT
