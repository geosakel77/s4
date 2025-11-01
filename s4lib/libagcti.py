from s4lib.libbase import Agent

class AgCTI(Agent):
    def __init__(self, agent_uuid, config, agent_type="CTI"):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)
        self.source_score={}
        self.cti_data_received={}
        self.cti_data_send={}
        self.rewards={}
        self.policies={}

    def sends_cti_product(self,src_uuid,product):
        destinations=[]
        for dm_uuid in self.connection_data_dm.keys():
            if self._get_decision(dm_uuid,product):
                destinations.append(dm_uuid)
                self._cti_product_sent(src_uuid,dm_uuid,product)
        self._calculate_source_score()
        return destinations

    def _cti_product_sent(self,dm_uuid,src_uuid,product):
        if src_uuid in self.cti_data_send.keys:
            if dm_uuid in self.cti_data_send[src_uuid].keys():
                self.cti_data_send[src_uuid][dm_uuid].append(product)
            else:
                self.cti_data_send[src_uuid][dm_uuid]=[product]
        else:
            self.cti_data_send[src_uuid]={dm_uuid:[product]}

    def receives_cti_product(self,src_uuid,product):
        if src_uuid in self.cti_data_received.keys():
            self.cti_data_received[src_uuid].append(product)
        else:
            self.cti_data_received[src_uuid]=[product]

    def _calculate_source_score(self):
        for src_uuid in self.cti_data_received.keys():
            total = sum(len(v) for v in self.cti_data_send[src_uuid].values())
            self.source_score[src_uuid]=total/len(self.cti_data_received[src_uuid])

    def get_source_score(self):
        return self.source_score

    def _get_decision(self,dm_uuid,product):
        decision=False
        if dm_uuid in self.policies.keys():
            decision=True
        return decision

    def get_rewards(self,dm_uuid,reward):
        if dm_uuid in self.rewards.keys():
            self.rewards[dm_uuid].append(reward)
        else:
            self.rewards[dm_uuid]=[reward]

    def policy_maker(self):

        pass

    def _update_time_actions(self):
        pass