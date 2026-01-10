from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.ppo import PPOConfig
from s4librl.librlctisrv import CTIRLServer
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
import gymnasium as gym
import numpy as np
from s4lib.libbase import read_from_json
import ray
from ray.tune.result import TRAINING_ITERATION

from ray.rllib.utils.metrics import (
    ENV_RUNNER_RESULTS,
    EPISODE_RETURN_MEAN,
    EVALUATION_RESULTS,
    NUM_ENV_STEPS_SAMPLED_LIFETIME,
)

def initialize_ray(config):
    rl_config = read_from_json(config["rl_config_path"])
    ray.init(
        num_cpus=rl_config['num-cpus'] or None,
        local_mode=rl_config['local-mode'],
        ignore_reinit_error=True,
    )



class AgCTIAlgConf:
    def __init__(self,algorithm_code=1,rl_env_config_path=CONFIG_PATH,framework=2,log_level=0):
        self.s4config = read_config(rl_env_config_path)
        self.rl_config = read_from_json(self.s4config["rl_config_path"])
        self.rl_env_config = {"s4config": self.s4config}
        self.framework = self.rl_config["framework"][framework]
        self.old_api_stack=self.rl_config["old-api-stack"]
        self.algorithm_code = self.rl_config["algo"][0]
        self.log_level = self.rl_config["log-level"][log_level]
        self.generated_config = None
        self.build_config()


    def build_config(self):
        if self.algorithm_code is self.rl_config["algo"][0]:
            self.generated_config=self._build_ppo_config()
        elif self.algorithm_code is self.rl_config["algo"][1]:
            self.generated_config=self._build_dqn_config()
        self.generated_config.framework(self.framework)
        if self.old_api_stack:
            self.generated_config.api_stack(
                enable_rl_module_and_learner=False,
                enable_env_runner_and_connector_v2=False,
            )
        if self.rl_config['num-env-runners'] is not None:
            self.generated_config.env_runners(num_env_runners=self.rl_config['num-env-runners'])
        if self.rl_config['num-envs-per-env-runner'] is not None:
            self.generated_config.env_runners(num_envs_per_env_runner=self.rl_config['num-envs-per-env-runner'])
        if self.generated_config.enable_rl_module_and_learner:
            if self.rl_config['num-gpus'] is not None and self.rl_config['num-gpus'] > 0:
                raise ValueError(
                    "num-gpus is not supported on the new API stack! To train on "
                    "GPUs, num-gpus-per-learner=1 and "
                    "num-learners=[your number of available GPUs], instead."
                )
            num_gpus_available = ray.cluster_resources().get("GPU",0)
            num_actual_learners=(self.rl_config['num-learners']
                                 if self.rl_config['num-learners'] is not None
                                 else self.generated_config.num_learners ) or 1
            num_gpus_requested= (self.rl_config['num-gpus-per-learner'] or 0)*num_actual_learners
            num_gpus_needed_if_available=(
                self.rl_config['num-gpus-per-learner']
                if self.rl_config['num-gpus-per-learner'] is not None
                else 1)*num_actual_learners
            self.generated_config.resources(num_gpus=0)
            if self.rl_config['num-learners'] is not None:
                self.generated_config.learners(num_learners=self.rl_config['num-learners'])
            if self.rl_config['num-aggregator-actors-per-learner'] is not None:
                self.generated_config.learners(num_aggregator_actors_per_learner=(self.rl_config['num-aggregator-actors-per-learner']))
            if self.rl_config['num-gpus-per-learner'] is None:
                if num_gpus_available>=num_gpus_needed_if_available:
                    self.generated_config.learners(num_gpus_per_learner=1)
                else:
                    self.generated_config.learners(num_gpus_per_learner=0)
            elif num_gpus_available<num_gpus_requested:
                raise ValueError( "You are running your script with num-learners="
                    f"{self.rl_config['num-learners']} and num-gpus-per-learner="
                    f"{self.rl_config['num-gpus-per-learner']}, but your cluster only has "
                    f"{num_gpus_available} GPUs!")
            else:
                self.generated_config.learners(num_gpus_per_learner=self.rl_config['num-gpus-per-learner'])

            if self.rl_config['num-cpus-per-learner'] is not None:
                self.generated_config.learners(num_cpus_per_learner=self.rl_config['num-cpus-per-learner'])
        elif self.rl_config['num-gpus'] is not None:
            self.generated_config.resources(num_gpus=self.rl_config['num-gpus'])

        if self.log_level is not None:
            self.generated_config.debugging(log_level=self.log_level)

        #TODO Evaluation Setup






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

    def get_stopping_criteria(self):
        stop = {
            f"{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}":self.rl_config['stop-reward'],
            f"{ENV_RUNNER_RESULTS}/{NUM_ENV_STEPS_SAMPLED_LIFETIME}": (
                self.rl_config['stop-timesteps']
            ),
            TRAINING_ITERATION: self.rl_config['stop-iters']
        }
        return stop





if __name__ == "__main__":
    import pprint
    confs4=read_config(CONFIG_PATH)

    initialize_ray(confs4)
    alg_config = AgCTIAlgConf()
    base_config = alg_config.get_env_config()

    print(alg_config.get_stopping_criteria())
    pprint.pprint(base_config.to_dict())








