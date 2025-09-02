from libbase import  Agent
from dataclasses import dataclass
from typing import List, Tuple, Dict
import uuid
from s4config.libconstants import DM_TYPES

@dataclass(slots=True)
class Record:
    record_id: int
    record_type: str
    record_value: str

class Engine:
    def __init__(self):
        self.knowledge_base: Dict[int, Record] = {}
        self.knowledge_base_values: List[Record.record_value] = []

    def reasoning(self,value):
        answer=None
        if value in self.knowledge_base_values:
            for key, item in self.knowledge_base.items():
                if item.record_value == value:
                    answer=key
        return answer

    def update_knowledge_base(self,record: Record):
        if record.record_value not in self.knowledge_base_values:
            self.knowledge_base_values.append(record.record_value)
            new_id = int(uuid.uuid4())
            record.record_id = new_id
            self.knowledge_base[record.record_id] = record
        else:
            print("Record value already exists in knowledge_base")


class DM(Agent):
    def __init__(self,dm_agent_uuid,dm_type,dm_config,dm_agent_type="DM"):
        super().__init__(agent_uuid=dm_agent_uuid,agent_type=dm_agent_type,config=dm_config)
        self.dm_type=dm_type
        self.engine=Engine()

    def get_html_status_data(self):
        pass


class PreventionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[1]):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config)

    def _update_time_actions(self):
        pass

class DetectionDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[2]):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config)

    def _update_time_actions(self):
        pass

class ResponseDM(DM):
    def __init__(self,agent_uuid,config,dm_type=DM_TYPES[3]):
        super().__init__(dm_agent_uuid=agent_uuid,dm_type=dm_type,dm_config=config)

    def _update_time_actions(self):
        pass