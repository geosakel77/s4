import threading,time
from s4lib.apisrv.libapisrvsrc import APISRCServer
from s4lib.apisrv.libapisrvagcti import APIAGCTIServer
from s4lib.apisrv.libapisrvdm import APIResponseDMServer,APIDetectionDMServer,APIPreventionDMServer
from s4lib.apisrv.libapisrvis import APIISServer
import tracemalloc


if __name__ == '__main__':
    print("Starting Experiment")
    tracemalloc.start()
    srcagent1 = APISRCServer(agent_type="SRC",title="SRC Test Agent")
    ctiagent2 = APIAGCTIServer(agent_type="CTI", title="AgCTI Test Agent")
    #redmagent3=APIResponseDMServer(agent_type="DM", title="Response DM Agent")
    dedmagent4=APIDetectionDMServer(agent_type="DM", title="Detection DM Agent")
    #prdmagent5=APIPreventionDMServer(agent_type="DM", title="Prevention DM Agent")
    isagent6=APIISServer(agent_type="IS", title="IS Agent")
    t1 = threading.Thread(target=srcagent1.run)
    t2= threading.Thread(target=ctiagent2.run)
    #t3= threading.Thread(target=redmagent3.run)
    t4= threading.Thread(target=dedmagent4.run)
    #t5= threading.Thread(target=prdmagent5.run)
    t6= threading.Thread(target=isagent6.run)

    t1.start()
    time.sleep(4)
    t2.start()
    time.sleep(4)
    #t3.start()
    #time.sleep(4)
    t4.start()
    time.sleep(4)
    #t5.start()
    #time.sleep(4)
    t6.start()
    time.sleep(4)
