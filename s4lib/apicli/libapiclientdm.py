from s4lib.apicli.libapiclient import APIClient
from typing import Dict,Any

class APIClientAgDM(APIClient):

    def __init__(self) -> None:
        super().__init__()

    async def rewards_cti_agent(self, base_url,reward: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending CTI product to {base_url}")
            r = await cli.post("/rewards_cti_agent", json=reward)
            r.raise_for_status()
            return r.json()

    async def detect_indicator(self, base_url,decision: Dict[str, Any]) -> Dict[str, Any]:
        """POST / with Record JSON"""
        async with self._ensure_client(base_url) as cli:
            print(f"Sending CTI product to {base_url}")
            r = await cli.post("/indicator_detected", json=decision)
            r.raise_for_status()
            return r.json()

class APIClientAgDetectionDM(APIClientAgDM):
    def __init__(self) -> None:
        super().__init__()