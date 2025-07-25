from libbase import Agent

class Coordinator(Agent):

    def __init__(self):
        super().__init__(agent_type="COORD")
        self.server.port=self.config["coordinator_port"]
        self.connection_data_ta={}
        self.connection_data_dm={}
        self.connection_data_cti={}

