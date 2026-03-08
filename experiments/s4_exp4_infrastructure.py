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
import threading, datetime,time
from s4lib.apisrv.libapisrvsrc import APISRCServer
from s4lib.apisrv.libapisrvagcti import APIAGCTIServer
from s4lib.apisrv.libapisrvdm import APIResponseDMServer, APIDetectionDMServer, APIPreventionDMServer
from s4lib.apisrv.libapisrvis import APIISServer
from s4lib.apisrv.libapisrvta import APITAServer
from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
import tracemalloc,os

if __name__ == '__main__':
    print("Starting experiment....")
    config_data = read_config(CONFIG_PATH)
    tracemalloc.start()
    #CTI Source Agents
    agents=[]
    for i in range(10):
        agents.append(APISRCServer(agent_type="SRC", title=f"SRC Agent {i}"))

    #CTI Agent
    for i in range(1):
        agents.append(APIAGCTIServer(agent_type="CTI", title=f"AgCTI Agent {i}"))
    #DM Agents
    for i in range(2):
        agents.append(APIResponseDMServer(agent_type="DM", title=f"Response DM Agent {i}"))

    for i in range(2):
        agents.append(APIDetectionDMServer(agent_type="DM", title=f"Detection DM Agent {i}"))

    for i in range(2):
        agents.append(APIPreventionDMServer(agent_type="DM", title=f"Prevention DM Agent {i}"))

    # IA Agents
    for i in range(20):
        agents.append(APIISServer(agent_type="IS", title=f"IS Agent {i}"))

    # TA Agents
    for i in range(1):
        agents.append(APITAServer(agent_type="TA", title=f"TA Agent {i}"))

    threading_agents=[]
    for agent in agents:
        threading_agents.append(threading.Thread(target=agent.run))

    for thread_agent in threading_agents:
        thread_agent.start()
        time.sleep(4)

    snapshot = tracemalloc.take_snapshot()
    os.makedirs(os.path.join(config_data['experiment_results_path'], config_data["exp_code"]), exist_ok=True)
    exp_filename = f"memory_{config_data['rl_agent_type']}.dat"
    file_path = os.path.join(config_data['experiment_results_path'], config_data["exp_code"], exp_filename)
    snapshot.dump(str(file_path))