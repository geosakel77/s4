from s4lib.apicli.libapiclient import APIClient
from typing import Dict,Any

class APIClientAgTA(APIClient):

    def __init__(self) -> None:
        super().__init__()

    async def execute_attack_step(self, base_url,cti_product: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending CTI product to {base_url}")
            r = await cli.post("/receive_ta_indicator", json=cti_product)
            r.raise_for_status()
            return r.json()