import time
import uuid,asyncio

from s4lib.libbase import Agent
from s4lib.libapiclient import APIClient
from s4lib.libapiserver import APIBaseServer, APIISServer
import threading





if __name__ == '__main__':

    testagent3 = APIISServer(agent_type="IS", title="IS Test Agent")

    t3=threading.Thread(target=testagent3.run)


    t3.start()
