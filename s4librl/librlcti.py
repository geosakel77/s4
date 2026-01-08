from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.ppo import PPOConfig
from s4librl.librlctisrv import CTIRLServer
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
import gymnasium as gym
import numpy as np


ALGORITHMS_NAMES={1:"PPO",2:"DQN"}



class AgCTIAlgConf:
    def __init__(self,algorithm_code=1,rl_env_config_path=CONFIG_PATH):
        self.s4config = read_config(rl_env_config_path)
        self.rl_env_config = {"s4config": self.s4config}
        self.algorithm_code = ALGORITHMS_NAMES[algorithm_code]
        self.generated_config = None
        if self.algorithm_code is ALGORITHMS_NAMES[1]:
            self.generated_config=self._build_ppo_config()
        elif self.algorithm_code is ALGORITHMS_NAMES[2]:
            self.generated_config=self._build_dqn_config()

    def _build_ppo_config(self):

        base_config = (
            PPOConfig().
            environment(
                observation_space=gym.spaces.Box(
                float("-inf"), float("-inf"), (4,), np.float32
                ),
                action_space=gym.spaces.Discrete(2),
                env_config=self.rl_env_config,
            )
            .env_runners(env_runner_cls=CTIRLServer,)
            .training(
                num_epochs=10,
                vf_loss_coeff=0.01,
            )
            .rl_module(model_config=DefaultModelConfig(vf_share_layers=True)))
        #Default Model Config to be changed with a custom using RLModelSpec
        return base_config

    def _build_dqn_config(self):
        base_config = ()
        return base_config

    def _build_expected_sarsa_config(self):
        base_config = ()
        return base_config

    def get_env_config(self):
        return self.generated_config

if __name__ == "__main__":
    pass










