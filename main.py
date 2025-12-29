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
