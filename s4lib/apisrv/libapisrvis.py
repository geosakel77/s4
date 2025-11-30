from s4lib.libis import IS
from fastapi import Request
from fastapi.responses import HTMLResponse
from s4lib.apisrv.libapiserver import APIBaseServer
from typing import Dict,Any

class APIISServer(APIBaseServer):

    def __init__(self,agent_type="IS",title="") -> None:
        super().__init__(agent_type,title)
        self.agent=IS(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_is_routes()

    def _register_is_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("is_status.html",{"request": request,"data":self.agent.get_html_status_data()})

        @self.app.post("/receives_ta_indicator")
        async def receives_ta_indicator(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid): f"Product has not received yet."}
            for key, value in update_data.items():
                response = self.agent.handle_indicator_from_ta(key,value)
            return response

