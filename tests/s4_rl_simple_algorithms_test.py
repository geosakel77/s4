from s4librl.simple.librlqlearning import QLearningAgentX

from s4librl.simple.librlenvironment import CTIAgentRLEnvironment
from s4librl.simple.librlexpectedsarsa import ExpectedSarsaAgent
from s4librl.utils import CTIAgentRLObservationsGenerator,CTIAgentRewardsGenerator
from s4lib.libbase import read_from_json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH

"""
def test_qlearning_algorithm():
    print("Testing q-learning algorithm")
    actions=[]
    agent_info = {"num_states": 3, "num_actions": 4, "epsilon": 0.1,"discount": 1.0,"seed": 0,"step_size": 0.1}
    current_agent = QLearningAgent(agent_info)
    current_agent.agent_init()
    action = current_agent.agent_start(0)
    print("Action Value Estimates: \n", current_agent.q)
    print("Action:", action)
    actions.append(action)
    actions.append(current_agent.agent_step(2, 1))
    actions.append(current_agent.agent_step(0, 0))
    print("Action Value Estimates: \n", current_agent.q)
    print("Actions:", actions)
    actions.append(current_agent.agent_step(2, 1))
    current_agent.agent_end(1)
    print("Action Value Estimates: \n", current_agent.q)
    print("Actions:", actions)
"""
def test_expected_sarsa_algorithm():
    print("Testing expected sarsa algorithm")
    actions=[]
    agent_info = {"num_actions": 4, "num_states": 3, "epsilon": 0.1, "step_size": 0.1, "discount": 1.0, "seed": 0}
    current_agent = ExpectedSarsaAgent(agent_info)
    current_agent.agent_init()
    actions.append(current_agent.agent_start(0))
    actions.append(current_agent.agent_step(2, 1))
    actions.append(current_agent.agent_step(0, 0))
    print("Action Value Estimates: \n", current_agent.q)
    print("Actions:", actions)
    actions.append(current_agent.agent_step(2, 1))
    current_agent.agent_end(1)
    print("Action Value Estimates: \n", current_agent.q)
    print("Actions:", actions)



def  test_qlearning_algorithm():
    config=read_config(CONFIG_PATH)
    agent_info=read_from_json(config["rl_config_path_simple"])
    cti_agent_obs_generator=CTIAgentRLObservationsGenerator()
    cti_agent_reward_generator=CTIAgentRewardsGenerator()
    env = CTIAgentRLEnvironment()
    agent = QLearningAgentX(agent_info = agent_info)
    agent.agent_init()
    returns=[]
    for episode in range(config["rl_num_episodes"]):
        obs = cti_agent_obs_generator.generate_state_observation()
        observation=env.env_start(obs)
        a= agent.agent_start(observation)
        goal=0.0
        terminal =False
        while not terminal:
            r, obs2, terminal = env.env_step(action=a,reward=cti_agent_reward_generator.next_step(),env_info=cti_agent_obs_generator.generate_state_observation())
            goal=goal+r
            if terminal:
                agent.agent_end(reward=r)
                agent.agent_cleanup()
            else:
                agent.agent_step(reward=r,observation=obs2)
        returns.append(goal)
        if (episode + 1) % 20 == 0:
            print(f"Episode {episode + 1:4d} | return={goal: .3f} | Q_entries={agent.agent_message('get_num_q_entries')}")
    print(f"Episodes Goals:{returns}")
    print(f"Q Table:{agent.agent_message('get_q')}")
    print(f"Observations-Actions:{agent.agent_message('get_obs_action')}")

if __name__ == '__main__':
    test_qlearning_algorithm()