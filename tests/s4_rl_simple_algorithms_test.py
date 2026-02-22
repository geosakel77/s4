from s4librl.simple.librlqlearning import QLearningAgentX
from s4librl.simple.librlenvironment import CTIAgentRLEnvironment
from s4librl.simple.librlexpectedsarsa import ExpectedSarsaAgentX
from s4librl.simple.librldiscreteactorcritic import SoftMaxActorCriticX
from s4librl.utils import CTIAgentRLObservationsGenerator,CTIAgentRewardsGenerator
from s4lib.libbase import read_from_json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH

def test_discrete_actor_critic_algorithm(config_dic):
    print("Testing Discrete Actor Critic algorithm")
    agent_info = read_from_json(config_dic["rl_config_path_simple"])
    cti_agent_obs_generator = CTIAgentRLObservationsGenerator()
    cti_agent_reward_generator = CTIAgentRewardsGenerator()
    env = CTIAgentRLEnvironment()
    agent = SoftMaxActorCriticX(agent_info=agent_info)
    agent.agent_init()
    returns = []
    for episode in range(config_dic["rl_num_episodes"]):
        obs = cti_agent_obs_generator.generate_state_observation()
        observation = env.env_start(obs)
        a = agent.agent_start(observation)
        goal = 0.0
        terminal = False
        while not terminal:
            r, obs2, terminal = env.env_step(action=a, reward=cti_agent_reward_generator.next_step(),
                                             env_info=cti_agent_obs_generator.generate_state_observation())
            goal = goal + r
            if terminal:
                agent.agent_end(reward=r)
                agent.agent_cleanup()
            else:
                agent.agent_step(reward=r, observation=obs2)
        returns.append(goal)
        if (episode + 1) % 20 == 0:
            print(
                f"Episode {episode + 1:4d} | return={goal: .3f} | Q_entries={agent.agent_message('get_shapes')}")

    print(f"Episodes Goals:{returns}")
    print(f"W_pi Table:{agent.agent_message('get_w_pi')}")
    print(f"Observations-Actions:{agent.agent_message('get_obs_action')}")

def test_expected_sarsa_algorithm(config_dic):
    print("Testing Expected Sarsa algorithm")
    agent_info=read_from_json(config_dic["rl_config_path_simple"])
    cti_agent_obs_generator=CTIAgentRLObservationsGenerator()
    cti_agent_reward_generator=CTIAgentRewardsGenerator()
    env = CTIAgentRLEnvironment()
    agent = ExpectedSarsaAgentX(agent_info = agent_info)
    agent.agent_init()
    returns=[]
    for episode in range(config_dic["rl_num_episodes"]):
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

def  test_qlearning_algorithm(config_dic):
    print("Testing Q-learning algorithm")
    agent_info=read_from_json(config_dic["rl_config_path_simple"])
    cti_agent_obs_generator=CTIAgentRLObservationsGenerator()
    cti_agent_reward_generator=CTIAgentRewardsGenerator()
    env = CTIAgentRLEnvironment()
    agent = QLearningAgentX(agent_info = agent_info)
    agent.agent_init()
    returns=[]
    for episode in range(config_dic["rl_num_episodes"]):
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
    config_dic = read_config(CONFIG_PATH)
    test_qlearning_algorithm(config_dic)
    #test_expected_sarsa_algorithm(config_dic)
    #test_discrete_actor_critic_algorithm(config_dic)