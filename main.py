import threading,time
from s4lib.apisrv.libapisrvsrc import APISRCServer
from s4lib.apisrv.libapisrvagcti import APIAGCTIServer


if __name__ == '__main__':
    print("Starting Experiment")

    srcagent1 = APISRCServer(agent_type="SRC",title="SRC Test Agent")
    ctiagent2 = APIAGCTIServer(agent_type="CTI", title="AgCTI Test Agent")
    #testagent3 = APIBaseServer(agent_type="IS", port=0, title="TA Test Agent")
    #testagent4 = APIBaseServer(agent_type="DM", port=0, title="TA Test Agent")
    #t=threading.Thread(target=testagent1.run)
    t1 = threading.Thread(target=srcagent1.run)
    t2= threading.Thread(target=ctiagent2.run)
    #t2=threading.Thread(target=testagent2.run)
    #t3=threading.Thread(target=testagent3.run)
    #t4=threading.Thread(target=testagent4.run)

    t1.start()
    time.sleep(4)
    t2.start()
    time.sleep(4)
    #t3.start()
    #time.sleep(4)
    #t4.start()