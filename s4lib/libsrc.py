from s4lib.libbase import Agent,read_from_json
from s4lib.libdm import Record
import random


class CTISRC(Agent):
    def __init__(self, agent_uuid, config, agent_type='SRC'):
        super().__init__(agent_uuid=agent_uuid, agent_type=agent_type, config=config)
        self.cti_data= self._sample_cti_data()

    def _sample_cti_data(self):
        cti_data_pool=read_from_json(self.config['cti_data_pool'])
        num_items= random.randint(int(len(cti_data_pool)/3),int(len(cti_data_pool)/2))
        selected_keys=random.sample(list(cti_data_pool.keys()),num_items)
        cti_sample_data={}
        for key in selected_keys:
            if cti_data_pool[key]['type']=='indicator':
                record_id = cti_data_pool[key]['id']
                record_type = cti_data_pool[key]['type']
                value = cti_data_pool[key]['pattern'].replace("'",'').replace('"','')
                new_record = Record(record_id, record_type, value)
                cti_sample_data[key]=new_record
            elif cti_data_pool[key]['type']=='vulnerability':
                record_id = cti_data_pool[key]['id']
                record_type = cti_data_pool[key]['type']
                value = cti_data_pool[key]['name'].replace("'",'').replace('"','')
                new_record = Record(record_id, record_type, value)
                cti_sample_data[key]=new_record
        return cti_sample_data

    def sharing_cti_data(self):
        if self.cti_data:
            shared_cti_product=self.cti_data.popitem()
        else:
            self.cti_data=self._sample_cti_data()
            shared_cti_product=self.cti_data.popitem()
        return shared_cti_product

    def _update_time_actions(self):

        pass


if __name__=='__main__':
    from s4config.libconstants import CONFIG_PATH
    from s4config.libconfig import read_config
    config = read_config(CONFIG_PATH)
    ctisrc = CTISRC(agent_uuid='SRC', config=config)
    print(ctisrc.sharing_cti_data())
    print(ctisrc.sharing_cti_data())