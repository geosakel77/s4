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
from s4lib.libdm import PreventionDM, DetectionDM, ResponseDM, DM, Record
from fastapi import Request
from fastapi.responses import HTMLResponse
from s4lib.apisrv.libapiserver import APIBaseServer
from typing import Dict,Any


class APIDMServer(APIBaseServer):

    def __init__(self,agent_type="DM",title="") -> None:
        super().__init__(agent_type,title)
        self.agent = None #DM(dm_agent_uuid=self.agent_uuid,dm_agent_type=self.agent_type,dm_config=self.config,dm_type=None)
        self._register_dm_routes()

    def _register_dm_routes(self) -> None:

        @self.app.post("/receives_cti_product")
        async def receives_cti_product(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid):f"Product has not received yet."}
            for key,product in update_data.items():
                response = self.agent.handle_indicator_from_agcti(Record(product['id'],product['type'],product['pattern']))
            return response

        @self.app.post("/receives_ta_indicator")
        async def receives_ta_indicator(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid): f"Product has not received yet."}
            for key, value in update_data.items():
                response = self.agent.handle_indicator_from_ta(value)
            return response

        @self.app.post("/evaluate_is_indicator")
        async def evaluate_is_indicator(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid): f"Product has not received yet."}
            for key, value in update_data.items():
                response = self.agent.handle_indicator_from_is(is_uuid=key,indicator=value)
            return response

        @self.app.post("/receives_value_and_state")
        async def receives_value_and_state(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = {str(self.agent.uuid): f"Value and state have not received yet."}
            for key, value in update_data.items():
                response = self.agent.receives_value_and_sate(is_uuid=key, value=value)
            return response


class APIPreventionDMServer(APIDMServer):
    def __init__(self,agent_type="DM",title="") -> None:
        super().__init__(agent_type,title)
        self.agent =PreventionDM(agent_uuid=self.agent_uuid,config=self.config)
        self._register_prevention_dm_routes()

    def _register_prevention_dm_routes(self) -> None:
        @self.app.get("/status", response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("prevention_dm_status.html",
                                                   {"request": request, "data": self.agent.get_html_status_data()})

class APIDetectionDMServer(APIDMServer):
    def __init__(self,agent_type="DM",title="") -> None:
        super().__init__(agent_type,title)
        self.agent =DetectionDM(agent_uuid=self.agent_uuid,config=self.config)
        self._register_detection_dm_routes()

    def _register_detection_dm_routes(self) -> None:
        @self.app.get("/status", response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("detection_dm_status.html",
                                                   {"request": request, "data": self.agent.get_html_status_data()})

class APIResponseDMServer(APIDMServer):
    def __init__(self,agent_type="DM",title="") -> None:
        super().__init__(agent_type,title)
        self.agent =ResponseDM(agent_uuid=self.agent_uuid,config=self.config)
        self._register_response_dm_routes()

    def _register_response_dm_routes(self) -> None:
        @self.app.get("/status", response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("response_dm_status.html",
                                                   {"request": request, "data": self.agent.get_html_status_data()})


