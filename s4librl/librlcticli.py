from ray.rllib.env.external.rllink import RLlink,get_rllink_message,send_rllink_message
from ray.rllib.core import COMPONENT_RL_MODULE,Columns
from ray.rllib.env.single_agent_episode import SingleAgentEpisode
import socket, time,pickle
import gymnasium as gym
import numpy as np
from ray.rllib.utils.numpy import softmax
from ray.rllib.utils.framework import try_import_torch

class CTIRLClient:
    def __init__(self,config):
        self.config = config
        self.rl_socket=None
        self.rl_module = None
        self.env = None
        self.torch, _ = try_import_torch()

    def _set_state(self,msg_body):
        self.rl_module.set_state(msg_body)

    def _connect_to_rl_server(self):
        while True:
            try:
                self.rl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.rl_socket.connect((self.config["rl_server_ip"],self.config["rl_server_port"]))
                break
            except ConnectionRefusedError:
                time.sleep(5)

    def send_message(self,message):
        send_rllink_message(self.rl_socket,message)
        msg_type,msg_body=get_rllink_message(self.rl_socket)
        return msg_type,msg_body


    def run(self):
        self._connect_to_rl_server()
        print("Checking Connection. Pinging RL Server")
        msg_type,msg_body=self.send_message({"type":RLlink.PING.name})
        print(f"{msg_type} : {msg_body}")
        print("Requesting Configuration")
        msg_type1,msg_body1=self.send_message({"type":RLlink.GET_CONFIG.name})
        print(f"{msg_type1} : {msg_body1}")
        print("Creating Configuration")
        rl_config = pickle.loads(msg_body1["config"])
        print("Creating RL Module")
        self.rl_module = rl_config.get_rl_module_spec().build()
        print("Requesting state/weights")
        msg_type2,msg_body2=self.send_message({"type":RLlink.GET_STATE.name})
        print(f"{msg_type2} : {msg_body2}")
        self._set_state(msg_body2["state"])
        env_steps_per_sample = rl_config.get_rollout_fragment_length()
        print("Starting Env Loop")

        self.env = gym.make("CartPole-v1")
        obs, _ = self.env.reset()
        episode = SingleAgentEpisode(observations=[obs])
        episodes = [episode]

        while True:
            # Perform action inference using the RLModule.
            logits = self.rl_module.forward_exploration(
                batch={
                    Columns.OBS: self.torch.tensor(np.array([obs], np.float32)),
                }
            )[Columns.ACTION_DIST_INPUTS][
                0
            ].numpy()  # [0]=batch size 1

            # Stochastic sample.
            action_probs = softmax(logits)
            action = int(np.random.choice(list(range(self.env.action_space.n)), p=action_probs))
            logp = float(np.log(action_probs[action]))

            # Perform the env step.
            obs, reward, terminated, truncated, _ = self.env.step(action)

            # Collect step data.
            episode.add_env_step(
                action=action,
                reward=reward,
                observation=obs,
                terminated=terminated,
                truncated=truncated,
                extra_model_outputs={
                    Columns.ACTION_DIST_INPUTS: logits,
                    Columns.ACTION_LOGP: logp,
                },
            )

            # We collected enough samples -> Send them to server.
            if sum(map(len, episodes)) == env_steps_per_sample:
                # Send the data to the server.

                message={
                        "type": RLlink.EPISODES_AND_GET_STATE.name,
                        "episodes": [e.get_state() for e in episodes],
                        "timesteps": env_steps_per_sample,
                        }
                # We are forced to sample on-policy. Have to wait for a response
                # with the state (weights) in it.
                msg_type, msg_body = self.send_message(message)
                print(f"{msg_type} : {msg_body}")
                self._set_state(msg_body["state"])
                episodes = []
                if not episode.is_done:
                    episode = episode.cut()
                    episodes.append(episode)

            # If episode is done, reset env and create a new episode.
            if episode.is_done:
                obs, _ = self.env.reset()
                episode = SingleAgentEpisode(observations=[obs])
                episodes.append(episode)