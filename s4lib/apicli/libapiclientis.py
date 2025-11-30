from s4lib.apicli.libapiclient import APIClient
from typing import Dict,Any

class APIClientAgIS(APIClient):

    def __init__(self) -> None:
        super().__init__()

    async def evaluate_indicator(self, base_url,cti_product: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending CTI product to {base_url}")
            r = await cli.post("/evaluate_is_indicator", json=cti_product)
            r.raise_for_status()
            return r.json()