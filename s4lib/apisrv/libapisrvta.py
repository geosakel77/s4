from s4lib.libta import TA
from fastapi import Request
from s4lib.apisrv.libapiserver import APIBaseServer
from fastapi.responses import HTMLResponse



class APITAServer(APIBaseServer):
    def __init__(self,agent_type="TA",title="TA API Server",actor_name=None) -> None:
        super().__init__(agent_type,title)
        self.agent=TA(ta_agent_uuid=self.agent_uuid,agent_type=self.agent_type,ta_config=self.config,actor_name=actor_name)
        self._register_ta_routes()

    def _register_ta_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("ta_status.html",{"request": request,"data":self.agent.get_html_status_data()})