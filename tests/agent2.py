from s4lib.apisrv.libapiserver import APIISServer, APITAServer
import threading





if __name__ == '__main__':

    testagent3 = APIISServer(agent_type="IS", title="IS Test Agent")
    testagent2= APITAServer(agent_type="TA", title="TA Test Agent",actor_name='Gamaredon Group')
    t3=threading.Thread(target=testagent3.run)
    t2=threading.Thread(target=testagent2.run)

    t3.start()
    t2.start()
