from libbase import  Agent


class DM(Agent):
    def __init__(self,dm_type,agent_type="DM"):
        super().__init__(agent_type)
        self.dm_type=dm_type



class PreventionDM(DM):
    def __init__(self,dm_type="Prevention"):
        super().__init__(dm_type)


class DetectionDM(DM):
    def __init__(self,dm_type="Detection"):
        super().__init__(dm_type)

class ResponseDM(DM):
    def __init__(self,dm_type="Response"):
        super().__init__(dm_type)
