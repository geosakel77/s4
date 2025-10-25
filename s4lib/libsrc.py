from s4lib.libbase import Agent




class CTISRC(Agent):
    def __init__(self, agent_uuid, config, agent_type='SRC'):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)


