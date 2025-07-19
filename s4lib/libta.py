from s4lib.libbase import AttackerAgent,read_from_json
import random


class TA(AttackerAgent):

    def __init__(self,agent_type="TA",actor_name=None):
        super().__init__(agent_type=agent_type)
        if actor_name is None:
            actors=read_from_json(self.config['actors_path'])
            self.actor_name= actors[random.choice(list(actors.keys()))]
        else:
            self.actor_name=actor_name
        self.actor = self._get_actor(self.actor_name)



    def _get_actor(self,actor_name):
        result=None
        for actor in self.mitre_attack.enterprise.actors:
            if actor.name == actor_name:
                result=actor
        return result

    def get_techniques(self):
        techniques=self.actor.techniques
        for technique in techniques:
            print(technique)
            break


    def get_external_references(self):
        external_references=self.actor.external_references
        for external_reference in external_references:
            print(external_reference)
        return external_references







if __name__ == "__main__":
    ta =TA(actor_name="APT29")
    print(ta.agent_type)
    ta.get_techniques()