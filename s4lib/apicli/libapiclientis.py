from s4lib.apicli.libapiclient import APIClient
from typing import Dict,Any

class APIClientAgIS(APIClient):

    def __init__(self) -> None:
        super().__init__()

    async def evaluate_indicator(self, base_url,indicators: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending Indicator to {base_url}")
            r = await cli.post("/evaluate_is_indicator", json=indicators)
            r.raise_for_status()
            return r.json()

    async def send_value_and_state(self, base_url,value_state: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending value and state {base_url}")
            r = await cli.post("/receives_value_and_state", json=value_state)
            r.raise_for_status()
            return r.json()
