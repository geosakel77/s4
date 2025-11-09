from s4lib.libbase import Agent
from s4lib.libdm import Record
from s4lib.apicli.libapiclientagcti import APIClientAgCTI
import random,string


def _get_random_key():
    return ''.join(random.choices(string.ascii_lowercase, k=6))


class AgCTI(Agent):
    def __init__(self, agent_uuid, config, agent_type="CTI"):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)
        self.source_score={}
        self.cti_data_current_pool={}
        self.cti_data_received={}
        self.cti_data_send={}
        self.rewards={}
        self.policies={}
        self.client=APIClientAgCTI()

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
            self.cti_data_received[src_uuid].append(Record(product['id'],product['type'],product['pattern']))
            self.cti_data_current_pool[_get_random_key()]={src_uuid:Record(product['id'], product['type'], product['pattern'])}
        else:
            self.cti_data_received[src_uuid]=[Record(product['id'],product['type'],product['pattern'])]
            self.cti_data_current_pool[_get_random_key()] = {src_uuid: Record(product['id'], product['type'], product['pattern'])}
        return {str(self.uuid):f"Product received from {src_uuid}"}

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
        return {str(self.uuid): f"Product received from {dm_uuid}"}


    def get_cti_product_received(self):
        product_received={}
        for key in self.cti_data_received.keys():
            product_received[key]=len(self.cti_data_received[key])
        return product_received

    def get_total_cti_product_received(self):
        total_cti_product_received=self.get_cti_product_received()
        total_number=0
        for key in total_cti_product_received.keys():
            total_number += total_cti_product_received[key]
        return total_number

    def get_cti_product_send(self):
        product_sent={}
        for key in self.cti_data_send.keys():
            product_sent[key]=len(self.cti_data_send[key])
        return product_sent

    def get_total_cti_product_send(self):
        total_cti_product_send=self.get_cti_product_send()
        total_number=0
        for key in total_cti_product_send.keys():
            total_number += total_cti_product_send[key]
        return total_number

    def get_policies(self):
        return self.policies

    def policy_maker(self):
        for key in self.connection_data_dm.keys():
            self.policies[key]=['Send all']
        #TODO

    async def _update_time_actions(self):
        self.policy_maker()
        product=self._pick_product()
        if product is not None:
            src_uuid,record=product.items()[0]
            destinations=self.sends_cti_product(src_uuid,record)
            for dm_uuid in destinations:
                connection_string= self.connection_data_dm[dm_uuid]
                if connection_string['host'] == "0.0.0.0":
                    dm_url = f"http://127.0.0.1:{connection_string['port']}"
                else:
                    dm_url = f"http://{connection_string['host']}:{connection_string['port']}"
                await self.client.send_cti_product(base_url=dm_url,cti_product={str(dm_uuid):record.serialize()})
        else:
            return {self.uuid:"Not ready yet"}

    def _pick_product(self):
        product=None
        if self.cti_data_current_pool:
            key,product=self.cti_data_current_pool.popitem()
        return product

    def get_html_status_data(self):
        html_status_data = {'id': self.uuid, 'source_score': self.get_source_score(), 'total_received':self.get_total_cti_product_received(),'total_sent':self.get_total_cti_product_send(),
                            'cti_product_received': self.get_cti_product_received(), 'cti_product_send':self.get_cti_product_send(),'policies':self.get_policies()}
        return html_status_data
