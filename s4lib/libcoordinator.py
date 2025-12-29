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

from s4lib.apicli.libapiclient import APIClientCoordinator
import random,uuid
from s4config.libconfig import read_config

registration_id_schema={
    "uuid":str,
    "agent_type":str,
    "host":str
}

class ConnectionString:
    host:str
    port:int
    agent_type:str
    uuid:str

    def get_connection_string(self):
        return {'host':self.host,'port':self.port,'agent_type':self.agent_type,'uuid':self.uuid}


class Coordinator:

    def __init__(self,configuration):
        self.id=uuid.uuid4()
        self.config = configuration
        self.connection_data_ta = {}
        self.connection_data_dm = {}
        self.connection_data_cti = {}
        self.connection_data_is = {}
        self.connection_data_src={}

        self.time_steps=self.config["time_steps"]
        self.registered_agents={}
        self.client=APIClientCoordinator()
        self.used_ports=[8000]
        self.status_data={'id':str(self.id),"ports":self.used_ports,"registered":self.registered_agents,"DM":self.connection_data_dm,"TA":self.connection_data_ta,"IS":self.connection_data_is,"CTI":self.connection_data_cti,"SRC":self.connection_data_src}

    def get_time(self):
        return self.time_steps

    def update_time(self):
        self.time_steps-=1

    def reset_time(self):
        self.time_steps=self.config["time_steps"]

    def _update_status(self):
        self.status_data = {'id': str(self.id), "ports": self.used_ports, "registered": self.registered_agents,
                            "DM": self.connection_data_dm, "TA": self.connection_data_ta, "IS": self.connection_data_is,
                            "CTI": self.connection_data_cti,"SRC":self.connection_data_src}

    def register_agent(self, reg_id):
        port = self._select_port()
        while port in self.used_ports:
            port = self._select_port()
        connection_string = ConnectionString()
        connection_string.host = reg_id['host']
        print(f"Host:{connection_string.host}")
        connection_string.port = port
        connection_string.agent_type = reg_id['agent_type']
        connection_string.uuid = reg_id['uuid']
        if reg_id['agent_type'] == "TA":
            self.connection_data_ta[reg_id['uuid']] = connection_string.get_connection_string()
        elif reg_id['agent_type'] == "CTI":
            self.connection_data_cti[reg_id['uuid']] = connection_string.get_connection_string()
        elif reg_id['agent_type'] == "DM":
            self.connection_data_dm[reg_id['uuid']] = connection_string.get_connection_string()
        elif reg_id['agent_type'] == "IS":
            self.connection_data_is[reg_id['uuid']] = connection_string.get_connection_string()
        elif reg_id['agent_type'] == "SRC":
            self.connection_data_src[reg_id['uuid']] = connection_string.get_connection_string()
        else:
            raise Exception("Unknown agent type")
        self.used_ports.append(port)
        if connection_string.host == "0.0.0.0":
            self.registered_agents[reg_id['uuid']] = f"http://127.0.0.1:{connection_string.port}"
        else:
            self.registered_agents[reg_id['uuid']] = f"http://{connection_string.host}:{connection_string.port}"
        self._update_status()
        return connection_string.get_connection_string()

    def update_agents(self,agent_uuid,response):
        try:
            status_code = response['status']
        except KeyError as e:
            status_code = None
        if status_code is None:
            conn_string= self.connection_data_ta.pop(agent_uuid,None)
            if conn_string is None:
                conn_string=self.connection_data_dm.pop(agent_uuid,None)
            if conn_string is None:
                conn_string=self.connection_data_cti.pop(agent_uuid,None)
            if conn_string is None:
                conn_string=self.connection_data_is.pop(agent_uuid,None)
            if conn_string is None:
                conn_string=self.connection_data_src.pop(agent_uuid,None)
            self.registered_agents.pop(agent_uuid,None)
            if conn_string is not None:
                self.used_ports.remove(conn_string['port'])
            self._update_status()

    def get_connection_info(self):
        conn_info = {"DM": self.connection_data_dm, "TA": self.connection_data_ta, "IS": self.connection_data_is,
                     "CTI": self.connection_data_cti,"SRC":self.connection_data_src,"RA":self.registered_agents}
        return conn_info
        #for agent_id in self.registered_agents.keys():
        #            #    self.client.update_agent(self.registered_agents[agent_id],conn_info)

    def _select_port(self):
        random_port = random.randint(8000,8100)
        while random_port in self.used_ports:
            random_port = random.randint(8000,8100)
        return random_port

    def get_html_status_data(self):
        html_status_data = self.status_data
        html_status_data['time_steps'] = self.time_steps
        html_status_data['current_time'] = self.config['time_steps'] - self.time_steps
        return html_status_data


if __name__ == "__main__":
    import uuid
    from s4config.libconstants import CONFIG_PATH
    config =read_config(CONFIG_PATH)
    coordinator = Coordinator(config)

    registration_id={'uuid': str(uuid.uuid4()), 'agent_type': 'TA'}
    registration_id1 = {'uuid': str(uuid.uuid4()), 'agent_type': 'CTI'}
    registration_id2= {'uuid': str(uuid.uuid4()), 'agent_type': 'DM'}
    registration_id3 = {'uuid': str(uuid.uuid4()), 'agent_type': 'IS'}

    print(coordinator.register_agent(registration_id))
    print(coordinator.register_agent(registration_id1))
    print(coordinator.register_agent(registration_id2))
    print(coordinator.register_agent(registration_id3))
