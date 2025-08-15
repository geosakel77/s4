import time
import uuid,asyncio

from s4lib.libbase import Agent
from s4lib.libapiclient import APIClient
from s4lib.libapiserver import APIBaseServer
import threading





if __name__ == '__main__':

    testagent1 = APIBaseServer(agent_type="TA", port=0, title="TA Test Agent")
    testagent2 = APIBaseServer(agent_type="CTI", port=0, title="TA Test Agent")
    testagent3 = APIBaseServer(agent_type="IS", port=0, title="TA Test Agent")
    testagent4 = APIBaseServer(agent_type="DM", port=0, title="TA Test Agent")
    t=threading.Thread(target=testagent1.run)

    t1=threading.Thread(target=testagent1.run)
    t2=threading.Thread(target=testagent2.run)
    t3=threading.Thread(target=testagent3.run)
    t4=threading.Thread(target=testagent4.run)

    t1.start()
    time.sleep(4)
    t2.start()
    time.sleep(4)
    t3.start()
    time.sleep(4)
    t4.start()