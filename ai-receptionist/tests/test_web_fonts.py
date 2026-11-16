"""The chat UI's self-hosted Inter: the two allowlisted files are served as woff2, and the
route exposes nothing else under web/."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import server

client = TestClient(server.app)


@pytest.mark.parametrize("name", ["inter-latin-opsz.woff2", "inter-latinext-opsz.woff2"])
def test_allowlisted_font_is_served(name: str) -> None:
    res = client.get(f"/fonts/{name}")
    assert res.status_code == 200
    assert res.headers["content-type"] == "font/woff2"
    assert res.content[:4] == b"wOF2"
    assert "max-age=" in res.headers["cache-control"]


@pytest.mark.parametrize("name", ["OFL-NOTICE.txt", "index.html", "..%2Fwidget.js", "x.woff2"])
def test_anything_else_is_404(name: str) -> None:
    assert client.get(f"/fonts/{name}").status_code == 404


def test_index_references_only_served_fonts() -> None:
    html = (server._WEB / "index.html").read_text()
    for name in server._FONTS:
        assert f"url('/fonts/{name}')" in html
    assert html.count("url('/fonts/") == len(server._FONTS)
