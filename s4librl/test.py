from s4librl.librlcti import AgCTIAlgConf
from ray.rllib.examples.utils import add_rllib_example_script_args,run_rllib_example_script_experiment
from s4librl.librlcticli import CTIRLClient
import threading
from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config

if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    alg_conf = AgCTIAlgConf(algorithm_code=1)
    base_config =alg_conf.get_env_config()

    parser = add_rllib_example_script_args(
        default_reward=450.0, default_iters=200, default_timesteps=2000000
    )

    parser.set_defaults(
        num_env_runners=1,
    )
    args = parser.parse_args()

    cti_rl_client = CTIRLClient(config)
    threading.Thread(target=cti_rl_client.run).start()

    run_rllib_example_script_experiment(base_config,args)
