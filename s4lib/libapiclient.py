from typing import Dict,Any
from contextlib import asynccontextmanager
import httpx



class APIClient:
    """Async client for APIServer."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.coordinator_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self,base_url) -> "APIClient":
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()

    async def health(self,base_url) -> Dict[str, Any]:
        """GET /health"""
        async with self._ensure_client(base_url) as cli:
            r = await cli.get("/health")
            r.raise_for_status()
            return r.json()

    async def echo(self, base_url,payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /echo with arbitrary JSON"""
        async with self._ensure_client(base_url) as cli:
            r = await cli.post("/echo", json=payload)
            r.raise_for_status()
            return r.json()


    @asynccontextmanager
    async def _ensure_client(self,base_url):
        """Use existing client if inside __aenter__, else create temp one."""
        if self._client:  # already in a with‑block
            yield self._client
        else:             # standalone call
            async with httpx.AsyncClient(base_url=base_url, timeout=10) as cli:
                yield cli



class APIRegistrationClient(APIClient):
    def __init__(self,coordinator_url: str = "http://127.0.0.1:8000") -> None:
       super().__init__(base_url=coordinator_url)


    async def register(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """POST /register with registration data JSON"""
        async with self._ensure_client(self.coordinator_url) as cli:
            response = await cli.post("/register", json=record)
            response.raise_for_status()
            return response.json()




class APIClientCoordinator(APIClient):
    def __init__(self) -> None:
        super().__init__()


    async def update_agent(self, server_url,connection_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /register with registration data JSON"""
        async with self._ensure_client(server_url) as cli:
            response = await cli.post("/update_agent", json=connection_data)
            response.raise_for_status()
            return response.json()

    async def check_health(self,server_url) -> Dict[str, Any]:
        """GET /register with registration data JSON"""
        async with self._ensure_client(server_url) as cli:
            response = await cli.get("/health")
            response.raise_for_status()
            return response.json()