from s4lib.libagcti import AgCTI
from fastapi import Request
from fastapi.responses import HTMLResponse
from s4lib.apisrv.libapiserver import APIBaseServer
from typing import Dict,Any

class APIAGCTIServer(APIBaseServer):

    def __init__(self,agent_type="CTI",title="") -> None:
        super().__init__(agent_type,title)
        self.agent=AgCTI(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_agcti_routes()

    def _register_agcti_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("agcti_status.html",{"request": request,"data":self.agent.get_html_status_data()})

        @self.app.post("/receives_cti_product")
        async def receives_cti_product(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid):f"Product has not received yet."}
            for key,value in update_data.items():
                response = self.agent.receives_cti_product(key,value)
            print(response)
            return response

        @self.app.post("/rewards_cti_agent")
        async def rewards_cti_agent(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid):f"Agent has not received reward yet."}
            for key,value in update_data.items():
                response = self.agent.get_rewards(key,value)
            print(response)
            return response
