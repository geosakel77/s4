import socket,time,os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import Dict,Any

from numpy.ma.core import absolute
from pygments.lexers import templates
from s4lib.libbase import Agent
from s4lib.libcoordinator import Coordinator,registration_id_schema
import uvicorn,uuid,asyncio
from config.libconstants import CONFIG_PATH
from config.libconfig import read_config
from s4lib.libapiclient import APIRegistrationClient
from s4lib.libbase import validate_schema
from s4lib.libis import IS
from s4lib.libta import TA


class APIServer:
    """
    Async HTTP server that exposes two endpoints:
      GET  /health    → {"status":"ok"}
      POST /echo      → {"received": <your JSON>}
    """

    def __init__(self,agent_type,host: str = "0.0.0.0", port: int = 8000,title="Async Echo API",config_path=CONFIG_PATH,local=True,lifespan=None) -> None:
        self.agent_type = agent_type
        self.agent_uuid = uuid.uuid4()
        self.config = read_config(config_path)
        self.agent=None
        if local:
            self.host = host
        else:
            self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.local = local
        if lifespan:
            self.app = FastAPI(title=title,lifespan=lifespan)
        else:
            self.app = FastAPI(title=title)
        self.app.mount("/static",StaticFiles(directory=os.path.abspath(self.config['static_path'])),name="static")
        self.templates = Jinja2Templates(directory=os.path.abspath(self.config['templates_path']))
        self._register_default_routes()

    def _register_default_routes(self) -> None:
        @self.app.get("/health")
        async def health() -> Dict[str, str]:
            return {"status": "ok","ID":str(self.agent_uuid)}

    def _register_routes(self) -> None:
        pass

    def run(self) -> None:
        """Block forever and serve HTTP until Ctrl‑C."""
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


class APIBaseServer(APIServer):

    def __init__(self,agent_type,title) -> None:
        super().__init__(agent_type=agent_type,title=title)
        self.coordinator_url = f"{self.config['coordinator_host']}:{self.config['coordinator_port']}"
        self.registration_client = APIRegistrationClient(coordinator_url=self.coordinator_url)
        self.registration_id = {'uuid': str(self.agent_uuid), 'agent_type': self.agent_type,'host': self.host}
        registration_response = asyncio.run(self.registration_client.register(self.registration_id))
        self.host = registration_response["host"]
        self.port = registration_response["port"]
        self.agent=Agent(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_routes()
        print(f"The server will run on {self.host}:{self.port}")

    def _register_routes(self) -> None:
        @self.app.post("/update_agent")
        async def update_agent(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response=self.agent.update_connection_data(update_data)
            return response

        @self.app.post("/update_time")
        async def update_time(req: Request) -> Dict[str, Any]:
            update_data = await req.json()
            response = self.agent.update_time(update_data)
            return response


class APIISServer(APIBaseServer):

    def __init__(self,agent_type="IS",title="") -> None:
        super().__init__(agent_type,title)
        self.agent=IS(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_is_routes()

    def _register_is_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("is_status.html",{"request": request,"data":self.agent.get_html_status_data()})

class APITAServer(APIBaseServer):
    def __init__(self,agent_type="TA",title="TA API Server") -> None:
        super().__init__(agent_type,title)
        self.agent=TA(agent_uuid=self.agent_uuid,agent_type=self.agent_type,config=self.config)
        self._register_ta_routes()

    def _register_ta_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("ta_status.html",{"request": request,"data":self.agent.get_html_status_data()})

class APIServerCoordinator(APIServer):

    def __init__(self, agent_type) -> None:
        super().__init__(agent_type,lifespan=self.lifespan)
        self._clock_task = None
        self._heartbeat_task = None
        self.coordinator_agent=Coordinator(configuration=self.config)
        self._register_routes()


    async def clock(self)-> None:
        while self.coordinator_agent.get_time()>0:
            absolute_time=self.coordinator_agent.config["time_steps"]-self.coordinator_agent.get_time()
            print(f"Clock Time: {absolute_time}")
            time_data={"current":absolute_time}
            for agent_uuid, agent_url in self.coordinator_agent.registered_agents.items():
                try:
                    update_time = await self.coordinator_agent.client.update_time(agent_url, time_data)
                    print(update_time)
                except Exception as e:
                    print(e)
            self.coordinator_agent.update_time()
            await asyncio.sleep(int(self.config['step_duration']))

    async def heartbeat(self) -> None:
        while True:
            print(f"[{time.strftime('%X')}] {self.agent_uuid} ❤️ Heartbeat: still alive")
            print(self.coordinator_agent.registered_agents)
            for agent_uuid, agent_url in self.coordinator_agent.registered_agents.items():
                try:
                    response = await self.coordinator_agent.client.check_health(agent_url)

                    self.coordinator_agent.update_agents(agent_uuid,response)
                    print(response)
                except Exception as e:
                    print(e)
            conn_info = self.coordinator_agent.get_connection_info()
            for agent_uuid, agent_url in self.coordinator_agent.registered_agents.items():
                try:
                    update_response = await self.coordinator_agent.client.update_agent(agent_url,conn_info)
                    print(update_response)
                except Exception as e:
                    print(e)
            await asyncio.sleep(int(self.config['heartbeat_rate']))


    def _register_routes(self) -> None:

        @self.app.get("/status",response_class=HTMLResponse)
        async def status(request: Request):
            return self.templates.TemplateResponse("status.html",{"request": request,"data":self.coordinator_agent.get_html_status_data()})

        @self.app.post("/register")
        async def register(req: Request) -> Dict[str, Any]:
            registration_id = await req.json()
            if validate_schema(registration_id, registration_id_schema):
                response=self.coordinator_agent.register_agent(registration_id)
            else:
                response={"status": "fail", "message": "The registration id is invalid"}
            return response

    @asynccontextmanager
    async def lifespan(self,app: FastAPI):
        self._heartbeat_task = asyncio.create_task(self.heartbeat())
        self._clock_task = asyncio.create_task(self.clock())
        print("Heartbeat and Clock task started")
        try:
            yield
        finally:
            print("Heartbeat task finished")
            self._heartbeat_task.cancel()
            self._clock_task.cancel()
            try:
                await self._heartbeat_task
                await self._clock_task
            except asyncio.CancelledError:
                print("Heartbeat and Clock stopped cleanly")





