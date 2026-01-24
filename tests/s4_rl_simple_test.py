from s4librl.simple.librlqlearning import QLearningAgent
from s4librl.simple.librlexpectedsarsa import ExpectedSarsaAgent


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

def test_cti_environment():
    print("Testing cti environment")
    actions=[]

if __name__ == '__main__':
    test_expected_sarsa_algorithm()