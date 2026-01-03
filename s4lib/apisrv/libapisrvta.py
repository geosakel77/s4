"""
Qualitative Assessment and Application of CTI based on Reinforcement Learning.
    Copyright (C) 2026  Georgios Sakellariou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
            status_data = self.agent.get_html_status_data()
            status_data['title'] = self.title
            return self.templates.TemplateResponse("ta_status.html",{"request": request,"data":status_data})