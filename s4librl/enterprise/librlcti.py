from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
from ray.rllib.algorithms.dqn import DQNConfig
from ray.rllib.algorithms.ppo import PPOConfig
from s4librl.enterprise.librlctisrv import CTIRLServer
from ray.rllib.core.rl_module.default_model_config import DefaultModelConfig
from ray.air.integrations.wandb import WandbLoggerCallback
import gymnasium as gym
import numpy as np
from s4lib.libbase import read_from_json
import ray,logging,os,time,json
from ray.tune.result import TRAINING_ITERATION
from ray.tune import CLIReporter
from ray import tune
from ray.rllib.utils.serialization import convert_numpy_to_python_primitives


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
    def __init__(self,algorithm_code=0,rl_env_config_path=CONFIG_PATH,framework=2,log_level=0,evaluation_duration_unit=0):
        self.s4config = read_config(rl_env_config_path)
        self.rl_config = read_from_json(self.s4config["rl_config_path"])
        self.rl_env_config = {"s4config": self.s4config}
        self.framework = self.rl_config["framework"][framework]
        self.old_api_stack=self.rl_config["old-api-stack"]
        self.algorithm_code = self.rl_config["algo"][algorithm_code]
        self.log_level = self.rl_config["log-level"][log_level]
        self.evaluation_duration_unit = self.rl_config["evaluation-duration-unit"][evaluation_duration_unit]
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

        if self.rl_config['evaluation-interval'] >0:
            if self.rl_config['evaluation-num-env-runners']>0:
                eval_paral_to_training = self.rl_config['evaluation-parallel-to-training']
            else:
                eval_paral_to_training = False
            self.generated_config.evaluation(
                evaluation_num_env_runners=self.rl_config['evaluation-num-env-runners'],
                evaluation_interval=self.rl_config['evaluation-interval'],
            evaluation_duration=self.rl_config['evaluation-duration'],
            evaluation_duration_unit=self.evaluation_duration_unit,
            evaluation_parallel_to_training=eval_paral_to_training,)


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
        base_config = (
            DQNConfig().
            environment(
                observation_space=gym.spaces.Box(
                    float("-inf"), float("-inf"), (4,), np.float32
                ),
                action_space=gym.spaces.Discrete(2),
                env_config=self.rl_env_config,
            )
            .env_runners(env_runner_cls=CTIRLServer, )
            .training(
                num_epochs=10,
                vf_loss_coeff=0.01,
            )
            .rl_module(model_config=DefaultModelConfig(vf_share_layers=True)))
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


class AgCTIAlgRunner:
    def __init__(self,rl_env_config_path=CONFIG_PATH,framework=2,log_level=1,evaluation_duration_unit=0):
        os.environ["CUDA_VISIBLE_DEVICES"] = "1"
        self.s4config = read_config(rl_env_config_path)
        self.rl_config = read_from_json(self.s4config["rl_config_path"])
        initialize_ray(self.s4config)
        self.algo_config=AgCTIAlgConf(rl_env_config_path=CONFIG_PATH,framework=framework,log_level=log_level,evaluation_duration_unit=evaluation_duration_unit)
        self.base_config=self.algo_config.get_env_config()
        self.stop=self.algo_config.get_stopping_criteria()
        self.logger=logging.getLogger(__name__)


    def run(self,keep_ray_up=False):
        if self.rl_config['no_tune']:
            assert  not self.rl_config['as-test'] and not self.rl_config['as-release-test']
            algo = self.base_config.build_algo()
            for i in range(self.stop.get(TRAINING_ITERATION, self.rl_config["stop-iters"])):
                results = algo.train()
                if ENV_RUNNER_RESULTS in results:
                    mean_return = results[ENV_RUNNER_RESULTS].get(EPISODE_RETURN_MEAN, np.nan)
                    print(f"iter={i} R={mean_return}", end="")
                    if (EVALUATION_RESULTS in results) and (ENV_RUNNER_RESULTS in results[EVALUATION_RESULTS]):
                        Reval = results[EVALUATION_RESULTS][ENV_RUNNER_RESULTS][EPISODE_RETURN_MEAN]
                        print(f" R(eval)={Reval}", end="")
                    for key, threshold in self.stop.items():
                        val = results
                        for k in key.split("/"):
                            try:
                                val = val[k]
                            except KeyError:
                                val = None
                                break
                        if val is not None and not np.isnan(val) and val >= threshold:
                            print(f"Stop criterium ({key}={threshold}) fulfilled!")
                            if not keep_ray_up:
                                ray.shutdown()
                            return results
                    if not keep_ray_up:
                        ray.shutdown()
                        return results
        else:
            return None

    def run_on_tune(self,tune_callbacks,wandb_active=True,progress_reporter=None, tune_max_report_freq=30,keep_ray_up=False,trainable=None,scheduler=None,success_metric=None):
        if self.rl_config['as-release-test']:
            self.rl_config['as-test'] = True

        if self.rl_config['as-test']:
            self.rl_config['verbose'] = 1
            tune_max_report_freq = 30

        tune_callbacks = tune_callbacks or []
        if wandb_active:
            wandb_key = self.rl_config['wandb-key']
            wandb_project = self.rl_config['wandb-project']
            tune_callbacks.append(WandbLoggerCallback(api_key=wandb_key, project=wandb_project,upload_checkpoints=True,**({"name":self.rl_config['wandb-run-name'] if self.rl_config['wandb-run-name'] is not None else {}})))

        if progress_reporter is None:
            if self.rl_config['num-agents'] == 0:
                progress_reporter = CLIReporter(
                    metric_columns={
                        TRAINING_ITERATION: "iter",
                        "time_total_s": "total time (s)",
                        NUM_ENV_STEPS_SAMPLED_LIFETIME: "ts",
                        f"{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}": "episode return mean",
                    },
                    max_report_frequency=tune_max_report_freq,
                )
            else:
                progress_reporter = CLIReporter(
                    metric_columns={
                        **{
                            TRAINING_ITERATION: "iter",
                            "time_total_s": "total time (s)",
                            NUM_ENV_STEPS_SAMPLED_LIFETIME: "ts",
                            f"{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}": "combined return",
                        },
                        **{
                            (
                                f"{ENV_RUNNER_RESULTS}/module_episode_returns_mean/{pid}"
                            ): f"return {pid}"
                            for pid in self.base_config.policies
                        },
                    },
                    max_report_frequency=tune_max_report_freq,
                )


        os.environ["RAY_AIR_NEW_OUTPUT"] = "0"
        start_time = time.time()
        results = tune.Tuner(trainable or self.base_config.algo_class,param_space=self.base_config,
            run_config=tune.RunConfig(
                stop=self.stop,
                verbose=self.rl_config["verbose"],
                callbacks=tune_callbacks,
                checkpoint_config=tune.CheckpointConfig(
                    checkpoint_frequency=self.rl_config['checkpoint-freq'],
                    checkpoint_at_end=self.rl_config['checkpoint-at-end'],
                ),
                progress_reporter=progress_reporter,
            ),
            tune_config=tune.TuneConfig(
                num_samples=self.rl_config['num-samples'],
                max_concurrent_trials=self.rl_config['max-concurrent-trials'],
                scheduler=scheduler,
            ),
        ).fit()
        time_taken = time.time() - start_time

        if not keep_ray_up:
            ray.shutdown()

        if results.errors:
            errors = [
                e.args[0].args[2]
                if e.args and hasattr(e.args[0], "args") and len(e.args[0].args) > 2
                else repr(e)
                for e in results.errors
            ]
            raise RuntimeError(
                f"Running the example script resulted in one or more errors! {errors}"
            )
        if self.rl_config['as-test']:
            results=self._testing_results(results=results,time_taken=time_taken,success_metric=success_metric)
        return results


    def _testing_results(self,results,time_taken,success_metric=None):

        test_passed = False
        if self.rl_config['as-test']:
            if success_metric is None:
                for try_it in [
                    f"{EVALUATION_RESULTS}/{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}",
                    f"{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}",
                ]:
                    if try_it in self.stop:
                        success_metric = {try_it: self.stop[try_it]}
                        break
                if success_metric is None:
                    success_metric = {
                        f"{ENV_RUNNER_RESULTS}/{EPISODE_RETURN_MEAN}": self.rl_config['stop_reward'],
                    }
            success_metric_key, success_metric_value = next(iter(success_metric.items()))
            best_value = max(
                row[success_metric_key] for _, row in results.get_dataframe().iterrows()
            )
            if best_value >= success_metric_value:
                test_passed = True
                print(f"`{success_metric_key}` of {success_metric_value} reached! ok")

            if self.rl_config['as-release-test']:
                trial = results._experiment_analysis.trials[0]
                stats = trial.last_result
                stats.pop("config", None)
                json_summary = {
                    "time_taken": float(time_taken),
                    "trial_states": [trial.status],
                    "last_update": float(time.time()),
                    "stats": convert_numpy_to_python_primitives(stats),
                    "passed": [test_passed],
                    "not_passed": [not test_passed],
                    "failures": {str(trial): 1} if not test_passed else {},
                }
                filename = os.environ.get("TEST_OUTPUT_JSON", "/tmp/learning_test.json")
                with open(filename, "wt") as f:
                    json.dump(json_summary, f)

            if not test_passed:
                raise ValueError(
                    f"`{success_metric_key}` of {success_metric_value} not reached!"
                )

        return results


if __name__ == "__main__":
    import pprint
    confs4=read_config(CONFIG_PATH)

    initialize_ray(confs4)
    alg_config = AgCTIAlgConf()
    base_config = alg_config.get_env_config()

    print(alg_config.get_stopping_criteria())
    pprint.pprint(base_config.to_dict())








