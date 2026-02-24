from sympy.physics.units import action

from s4librl.simple.librlqlearning import QLearningAgentX
from s4librl.simple.librlenvironment import CTIAgentRLEnvironment
from s4librl.simple.librlexpectedsarsa import ExpectedSarsaAgentX
from s4librl.simple.librldiscreteactorcritic import SoftMaxActorCriticX
from s4librl.utils import CTIAgentRLObservationsGenerator,CTIAgentRewardsGenerator
from s4lib.libbase import read_from_json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
from s4librl.librlagent import RLAgent
import uuid


def test_rl_agent(conf_dic):
    agent_info = read_from_json(config_dic["rl_config_path_simple"])
    cti_agent_obs_generator=CTIAgentRLObservationsGenerator()
    cti_agent_reward_generator=CTIAgentRewardsGenerator()
    rl_agent=RLAgent(config=config_dic,agent_info=agent_info,dm_uuid="aaa",dm_type=0,agcti_uuid="ccc")
    for i in range(0,5000):
        observation = cti_agent_obs_generator.generate_state_observation()
        record_id=str(uuid.uuid1())
        if i==0:
            rl_agent.agent_start(observation,record_id)
        else:
            rl_agent.agent_step(action=0,reward=cti_agent_reward_generator.next_step(),encoded_record=observation,record_id=record_id)
    print(rl_agent.get_status())


if __name__ == '__main__':
    config_dic = read_config(CONFIG_PATH)
    test_rl_agent(config_dic)
