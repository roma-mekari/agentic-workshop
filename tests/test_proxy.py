"""Unit tests for PokeProxy routes using mocked PokeAPI responses."""

import pytest
import httpx
from fastapi.testclient import TestClient

from pokeproxy.main import app


def _make_transport(status: int, body: dict) -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=body)

    return httpx.MockTransport(handler)


@pytest.fixture
def client_with_mock(monkeypatch):
    """Return a TestClient whose PokeAPI calls are intercepted."""

    def _factory(status: int, body: dict):
        mock_http = httpx.AsyncClient(
            base_url="https://pokeapi.co/api/v2",
            transport=_make_transport(status, body),
        )

        with TestClient(app) as tc:
            tc.app.state.http_client = mock_http
            yield tc

    return _factory


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health():
    with TestClient(app) as tc:
        r = tc.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /api/v1/pokemon/{name_or_id}
# ---------------------------------------------------------------------------

def test_get_pokemon_ok(client_with_mock):
    body = {"id": 1, "name": "bulbasaur"}
    for tc in client_with_mock(200, body):
        r = tc.get("/api/v1/pokemon/bulbasaur")
        assert r.status_code == 200
        assert r.json()["name"] == "bulbasaur"


def test_get_pokemon_not_found(client_with_mock):
    for tc in client_with_mock(404, {}):
        r = tc.get("/api/v1/pokemon/notapokemon")
        assert r.status_code == 404


def test_get_pokemon_upstream_error(client_with_mock):
    for tc in client_with_mock(500, {}):
        r = tc.get("/api/v1/pokemon/bulbasaur")
        assert r.status_code == 502


# ---------------------------------------------------------------------------
# GET /api/v1/pokemon (list)
# ---------------------------------------------------------------------------

def test_list_pokemon_ok(client_with_mock):
    body = {"count": 1302, "results": [{"name": "bulbasaur"}]}
    for tc in client_with_mock(200, body):
        r = tc.get("/api/v1/pokemon?limit=10&offset=0")
        assert r.status_code == 200
        assert "results" in r.json()


def test_list_pokemon_invalid_limit():
    with TestClient(app) as tc:
        r = tc.get("/api/v1/pokemon?limit=0")
    assert r.status_code == 400


def test_list_pokemon_invalid_offset():
    with TestClient(app) as tc:
        r = tc.get("/api/v1/pokemon?offset=-1")
    assert r.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/v1/type/{name_or_id}
# ---------------------------------------------------------------------------

def test_get_type_ok(client_with_mock):
    body = {"id": 1, "name": "normal"}
    for tc in client_with_mock(200, body):
        r = tc.get("/api/v1/type/normal")
        assert r.status_code == 200
        assert r.json()["name"] == "normal"


def test_get_type_not_found(client_with_mock):
    for tc in client_with_mock(404, {}):
        r = tc.get("/api/v1/type/nosuchtype")
        assert r.status_code == 404
