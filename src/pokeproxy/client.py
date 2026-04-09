"""HTTP client for PokeAPI."""

import httpx

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
_DEFAULT_TIMEOUT = 10.0


def build_client() -> httpx.AsyncClient:
    """Return a configured async HTTP client for PokeAPI."""
    return httpx.AsyncClient(
        base_url=POKEAPI_BASE_URL,
        timeout=_DEFAULT_TIMEOUT,
        headers={"Accept": "application/json"},
    )
