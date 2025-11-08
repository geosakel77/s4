from s4lib.libsrc import CTISRC
from fastapi import Request
from fastapi.responses import HTMLResponse
from s4lib.apisrv.libapiserver import APIBaseServer

class APISRCServer(APIBaseServer):

    def __init__(self,agent_type="SRC",title="") -> None:
        super().__init__(agent_type,title)
        self.agent=CTISRC(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_src_routes()

    def _register_src_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("src_status.html",{"request": request,"data":self.agent.get_html_status_data()})

