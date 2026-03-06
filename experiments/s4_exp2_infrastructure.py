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
import threading, time
from s4lib.apisrv.libapisrvsrc import APISRCServer
from s4lib.apisrv.libapisrvagcti import APIAGCTIServer
from s4lib.apisrv.libapisrvdm import APIResponseDMServer, APIDetectionDMServer, APIPreventionDMServer
from s4lib.apisrv.libapisrvis import APIISServer
from s4lib.apisrv.libapisrvta import APITAServer
import tracemalloc

if __name__ == '__main__':
    print("Starting experiment....")
    tracemalloc.start()
    #CTI Source Agents
    srcagent1 = APISRCServer(agent_type="SRC", title="SRC Agent 1")
    srcagent2 = APISRCServer(agent_type="SRC", title="SRC Agent 2")
    srcagent3 = APISRCServer(agent_type="SRC", title="SRC Agent 3")
    srcagent4 = APISRCServer(agent_type="SRC", title="SRC Agent 4")
    #srcagent5 = APISRCServer(agent_type="SRC", title="SRC Agent 5")
    #srcagent6 = APISRCServer(agent_type="SRC", title="SRC Agent 6")
    #srcagent7 = APISRCServer(agent_type="SRC", title="SRC Agent 7")
    #srcagent8 = APISRCServer(agent_type="SRC", title="SRC Agent 8")
    #srcagent9 = APISRCServer(agent_type="SRC", title="SRC Agent 9")
    #srcagent10 = APISRCServer(agent_type="SRC", title="SRC Agent 10")

    #CTI Agent
    ctiagent2 = APIAGCTIServer(agent_type="CTI", title="AgCTI Agent")

    #DM Agents
    redmagent1 = APIResponseDMServer(agent_type="DM", title="Response DM Agent 1")
    redmagent2 = APIResponseDMServer(agent_type="DM", title="Response DM Agent 2")

    dedmagent1 = APIDetectionDMServer(agent_type="DM", title="Detection DM Agent 1")
    dedmagent2 = APIDetectionDMServer(agent_type="DM", title="Detection DM Agent 2")

    prdmagent1 = APIPreventionDMServer(agent_type="DM", title="Prevention DM Agent 1")

    #IS Agents
    isagent1=APIISServer(agent_type="IS", title="IS Agent 1")
    isagent2=APIISServer(agent_type="IS", title="IS Agent 2")
    isagent3=APIISServer(agent_type="IS", title="IS Agent 3")
    isagent4=APIISServer(agent_type="IS", title="IS Agent 4")
    isagent5=APIISServer(agent_type="IS", title="IS Agent 5")
    isagent6=APIISServer(agent_type="IS", title="IS Agent 6")
    isagent7=APIISServer(agent_type="IS", title="IS Agent 7")
    isagent8=APIISServer(agent_type="IS", title="IS Agent 8")
    isagent9=APIISServer(agent_type="IS", title="IS Agent 9")
    isagent10=APIISServer(agent_type="IS", title="IS Agent 10")

    # TA Agents
    taagent7 =APITAServer(agent_type="TA", title="TA Agent")

    ts1=threading.Thread(target=srcagent1.run)
    ts2=threading.Thread(target=srcagent2.run)
    ts3=threading.Thread(target=srcagent3.run)
    ts4=threading.Thread(target=srcagent4.run)
    #ts5=threading.Thread(target=srcagent5.run)
    #ts6=threading.Thread(target=srcagent6.run)
    #ts7=threading.Thread(target=srcagent7.run)
    #ts8=threading.Thread(target=srcagent8.run)
    #ts9=threading.Thread(target=srcagent9.run)
    #ts10=threading.Thread(target=srcagent10.run)
    t2 = threading.Thread(target=ctiagent2.run)
    tr1 = threading.Thread(target=redmagent1.run)
    tr2 = threading.Thread(target=redmagent2.run)
    td1 = threading.Thread(target=dedmagent1.run)
    td2 = threading.Thread(target=dedmagent2.run)
    tp1 = threading.Thread(target=prdmagent1.run)
    ti1=threading.Thread(target=isagent1.run)
    ti2=threading.Thread(target=isagent2.run)
    ti3=threading.Thread(target=isagent3.run)
    ti4=threading.Thread(target=isagent4.run)
    ti5=threading.Thread(target=isagent5.run)
    ti6=threading.Thread(target=isagent6.run)
    ti7=threading.Thread(target=isagent7.run)
    ti8=threading.Thread(target=isagent8.run)
    ti9=threading.Thread(target=isagent9.run)
    ti10=threading.Thread(target=isagent10.run)
    t7 = threading.Thread(target=taagent7.run)

    ts1.start()
    time.sleep(4)
    ts2.start()
    time.sleep(4)
    ts3.start()
    time.sleep(4)
    ts4.start()
    time.sleep(4)
    #ts5.start()
    #time.sleep(4)
    #ts6.start()
    #time.sleep(4)
    #ts7.start()
    #time.sleep(4)
    #ts8.start()
    #time.sleep(4)
    #ts9.start()
    #time.sleep(4)
    #ts10.start()
    #time.sleep(4)
    t2.start()
    time.sleep(4)
    tp1.start()
    time.sleep(4)
    td1.start()
    time.sleep(4)
    td2.start()
    time.sleep(4)
    tr1.start()
    time.sleep(4)
    tr2.start()
    time.sleep(4)
    ti1.start()
    time.sleep(4)
    ti2.start()
    time.sleep(4)
    ti3.start()
    time.sleep(4)
    ti4.start()
    time.sleep(4)
    ti5.start()
    time.sleep(4)
    ti6.start()
    time.sleep(4)
    ti7.start()
    time.sleep(4)
    ti8.start()
    time.sleep(4)
    ti9.start()
    time.sleep(4)
    ti10.start()
    time.sleep(4)
    t7.start()
    #time.sleep(2)
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics("lineno")
    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)
