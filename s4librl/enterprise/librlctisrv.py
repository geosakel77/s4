import pickle
import socket
import threading
import time
from collections import defaultdict
from typing import Collection, DefaultDict, List, Optional, Union

from ray.rllib.core import (
    COMPONENT_RL_MODULE,
    DEFAULT_AGENT_ID,
    DEFAULT_MODULE_ID,
)
from ray.rllib.env import INPUT_ENV_SPACES
from ray.rllib.env.env_runner import EnvRunner
from ray.rllib.env.external.rllink import (
    RLlink,
    get_rllink_message,
    send_rllink_message,
)
from ray.rllib.env.single_agent_env_runner import SingleAgentEnvRunner
from ray.rllib.env.single_agent_episode import SingleAgentEpisode
from ray.rllib.utils.annotations import override
from ray.rllib.utils.checkpoints import Checkpointable
from ray.rllib.utils.framework import try_import_torch
from ray.rllib.utils.metrics import (
    EPISODE_DURATION_SEC_MEAN,
    EPISODE_LEN_MAX,
    EPISODE_LEN_MEAN,
    EPISODE_LEN_MIN,
    EPISODE_RETURN_MAX,
    EPISODE_RETURN_MEAN,
    EPISODE_RETURN_MIN,
    WEIGHTS_SEQ_NO,
)
from ray.rllib.utils.metrics.metrics_logger import MetricsLogger
from ray.rllib.utils.typing import EpisodeID, StateDict
from ray.util.annotations import DeveloperAPI

torch, _ = try_import_torch()




class CTIRLServer(EnvRunner,Checkpointable):
    def __init__(self, *,config,**kwargs):
        super().__init__(config=config,**kwargs)
        self.s4config = self.config.get('env_config',{}).get("s4config", {})
        self.worker_index: int =  kwargs.get("worker_index", 0)
        self._weights_seq_no = 0

        # Build the module from its spec.
        module_spec = self.config.get_rl_module_spec(
            spaces=self.get_spaces(), inference_only=True
        )
        self.module = module_spec.build()

        self.host = self.s4config["rl_server_ip"]
        self.port = self.s4config["rl_server_port"] + self.worker_index
        self.server_socket = None
        self.client_socket = None
        self.address = None

        self.metrics: MetricsLogger = MetricsLogger(
            stats_cls_lookup=config.stats_cls_lookup, root=False
        )

        self._episode_chunks_to_return: Optional[List[SingleAgentEpisode]] = None
        self._done_episodes_for_metrics: List[SingleAgentEpisode] = []
        self._ongoing_episodes_for_metrics: DefaultDict[
            EpisodeID, List[SingleAgentEpisode]
        ] = defaultdict(list)

        self._sample_lock = threading.Lock()
        self._on_policy_lock = threading.Lock()
        self._blocked_on_state = False

        # Start a background thread for client communication.
        self.thread = threading.Thread(
            target=self._client_message_listener, daemon=True
        )
        self.thread.start()

    def assert_healthy(self):
        """Checks that the server socket is open and listening."""
        assert (
            self.server_socket is not None
        ), "Server socket is None (not connected, not listening)."

    def sample(self, **kwargs):
        """Waits for the client to send episodes."""
        while True:
            with self._sample_lock:
                if self._episode_chunks_to_return is not None:
                    num_env_steps = 0
                    num_episodes_completed = 0
                    for eps in self._episode_chunks_to_return:
                        if eps.is_done:
                            self._done_episodes_for_metrics.append(eps)
                            num_episodes_completed += 1
                        else:
                            self._ongoing_episodes_for_metrics[eps.id_].append(eps)
                        num_env_steps += len(eps)

                    ret = self._episode_chunks_to_return
                    self._episode_chunks_to_return = None

                    SingleAgentEnvRunner._increase_sampled_metrics(self, num_env_steps, num_episodes_completed)

                    return ret
            time.sleep(0.01)

    def get_metrics(self):

        # Compute per-episode metrics (only on already completed episodes).
        for eps in self._done_episodes_for_metrics:
            assert eps.is_done
            episode_length = len(eps)
            episode_return = eps.get_return()
            episode_duration_s = eps.get_duration_s()
            # Don't forget about the already returned chunks of this episode.
            if eps.id_ in self._ongoing_episodes_for_metrics:
                for eps2 in self._ongoing_episodes_for_metrics[eps.id_]:
                    episode_length += len(eps2)
                    episode_return += eps2.get_return()
                    episode_duration_s += eps2.get_duration_s()
                del self._ongoing_episodes_for_metrics[eps.id_]

            self._log_episode_metrics(
                episode_length, episode_return, episode_duration_s
            )

        # Now that we have logged everything, clear cache of done episodes.
        self._done_episodes_for_metrics.clear()

        # Return reduced metrics.
        return self.metrics.reduce()

    def get_spaces(self):
        return {
            INPUT_ENV_SPACES: (self.config.observation_space, self.config.action_space),
            DEFAULT_MODULE_ID: (
                self.config.observation_space,
                self.config.action_space,
            ),
        }

    def stop(self):
        """Closes the client and server sockets."""
        self._close_sockets_if_necessary()

    def get_ctor_args_and_kwargs(self):
        return (
            (),  # *args
            {"config": self.config},  # **kwargs
        )

    def get_checkpointable_components(self):
        return [
            (COMPONENT_RL_MODULE, self.module),
        ]

    def get_state(
        self,
        components: Optional[Union[str, Collection[str]]] = None,
        *,
        not_components: Optional[Union[str, Collection[str]]] = None,
        **kwargs,
    ) -> StateDict:
        return {
            COMPONENT_RL_MODULE: self.module.get_state(),
            WEIGHTS_SEQ_NO: self._weights_seq_no,
        }

    def set_state(self, state: StateDict) -> None:
        # Update the RLModule state.
        if COMPONENT_RL_MODULE in state:
            # A missing value for WEIGHTS_SEQ_NO or a value of 0 means: Force the
            # update.
            weights_seq_no = state.get(WEIGHTS_SEQ_NO, 0)

            # Only update the weigths, if this is the first synchronization or
            # if the weights of this `EnvRunner` lacks behind the actual ones.
            if weights_seq_no == 0 or self._weights_seq_no < weights_seq_no:
                rl_module_state = state[COMPONENT_RL_MODULE]
                if (
                    isinstance(rl_module_state, dict)
                    and DEFAULT_MODULE_ID in rl_module_state
                ):
                    rl_module_state = rl_module_state[DEFAULT_MODULE_ID]
                self.module.set_state(rl_module_state)

            # Update our weights_seq_no, if the new one is > 0.
            if weights_seq_no > 0:
                self._weights_seq_no = weights_seq_no

        if self._blocked_on_state is True:
            self._send_set_state_message()
            self._blocked_on_state = False

    def _client_message_listener(self):
        """Entry point for the listener thread."""

        # Set up the server socket and bind to the specified host and port.
        self._recycle_sockets()

        # Enter an endless message receival- and processing loop.
        while True:
            # As long as we are blocked on a new state, sleep a bit and continue.
            # Do NOT process any incoming messages (until we send out the new state
            # back to the client).
            if self._blocked_on_state is True:
                time.sleep(0.01)
                continue

            try:
                # Blocking call to get next message.
                msg_type, msg_body = get_rllink_message(self.client_socket)

                # Process the message received based on its type.
                # Initial handshake.
                if msg_type == RLlink.PING:
                    self._send_pong_message()

                # Episode data from the client.
                elif msg_type in [
                    RLlink.EPISODES,
                    RLlink.EPISODES_AND_GET_STATE,
                ]:
                    self._process_episodes_message(msg_type, msg_body)

                # Client requests the state (model weights).
                elif msg_type == RLlink.GET_STATE:
                    self._send_set_state_message()

                # Clients requests config information.
                elif msg_type == RLlink.GET_CONFIG:
                    self._send_set_config_message()

            except ConnectionError as e:
                print(f"Messaging/connection error {e}! Recycling sockets ...")
                self._recycle_sockets(5.0)
                continue

    def _recycle_sockets(self, sleep: float = 0.0):
        # Close all old sockets, if they exist.
        self._close_sockets_if_necessary()

        time.sleep(sleep)

        # Start listening on the configured port.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of the address.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        # Listen for a single connection.
        self.server_socket.listen(1)
        print(f"Waiting for client to connect to port {self.port}...")

        self.client_socket, self.address = self.server_socket.accept()
        print(f"Connected to client at {self.address}")

    def _close_sockets_if_necessary(self):
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

    def _send_pong_message(self):
        send_rllink_message(self.client_socket, {"type": RLlink.PONG.name})

    def _process_episodes_message(self, msg_type, msg_body):
        # On-policy training -> we have to block until we get a new `set_state` call
        # (b/c the learning step is done and we can send new weights back to all
        # clients).
        if msg_type == RLlink.EPISODES_AND_GET_STATE:
            self._blocked_on_state = True

        episodes = []
        for episode_state in msg_body["episodes"]:
            episode = SingleAgentEpisode.from_state(episode_state)
            episodes.append(episode.to_numpy())

        # Push episodes into the to-be-returned list (for `sample()` requests).
        with self._sample_lock:
            if isinstance(self._episode_chunks_to_return, list):
                self._episode_chunks_to_return.extend(episodes)
            else:
                self._episode_chunks_to_return = episodes

    def _send_set_state_message(self):
        send_rllink_message(
            self.client_socket,
            {
                "type": RLlink.SET_STATE.name,
                "state": self.get_state(inference_only=True),
            },
        )

    def _send_set_config_message(self):
        send_rllink_message(
            self.client_socket,
            {
                "type": RLlink.SET_CONFIG.name,
                "config": pickle.dumps(self.config),
            },
        )

    def _log_episode_metrics(self, length, ret, sec):
        # Log general episode metrics.
        # To mimic the old API stack behavior, we'll use `window` here for
        # these particular stats (instead of the default EMA).
        win = self.config.metrics_num_episodes_for_smoothing
        self.metrics.log_value(EPISODE_LEN_MEAN, length, window=win)
        self.metrics.log_value(EPISODE_RETURN_MEAN, ret, window=win)
        self.metrics.log_value(EPISODE_DURATION_SEC_MEAN, sec, window=win)
        # Per-agent returns.
        self.metrics.log_value(
            ("agent_episode_returns_mean", DEFAULT_AGENT_ID), ret, window=win
        )
        # Per-RLModule returns.
        self.metrics.log_value(
            ("module_episode_returns_mean", DEFAULT_MODULE_ID), ret, window=win
        )

        # For some metrics, log min/max as well.
        self.metrics.log_value(EPISODE_LEN_MIN, length, reduce="min", window=win)
        self.metrics.log_value(EPISODE_RETURN_MIN, ret, reduce="min", window=win)
        self.metrics.log_value(EPISODE_LEN_MAX, length, reduce="max", window=win)
        self.metrics.log_value(EPISODE_RETURN_MAX, ret, reduce="max", window=win)





