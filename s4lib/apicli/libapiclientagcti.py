from s4lib.apicli.libapiclient import APIClient
from typing import Dict,Any

class APIClientAgCTI(APIClient):

    def __init__(self) -> None:
        super().__init__()

    async def send_cti_product(self, base_url,cti_product: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending CTI product to {base_url}")
            r = await cli.post("/receives_cti_product", json=cti_product)
            r.raise_for_status()
            return r.json()