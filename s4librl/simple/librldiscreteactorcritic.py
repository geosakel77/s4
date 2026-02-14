"""
    Qualitative Assessment and Application of CTI based on Reinforcement Learning.

    Copyright (C) 2026  Georgios Sakellariou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations
from s4librl.simple.librlbaseagent import BaseAgent
from s4librl.simple.utils import StateEncoderXDSAC
from typing import Dict, Any
import numpy as np

def stable_softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits)
    ez = np.exp(z)
    return ez / np.sum(ez)

class SoftMaxActorCriticX(BaseAgent):

    def __init__(self, agent_info):
        super().__init__()
        self.num_actions = None
        self.alpha_pi = None
        self.alpha_v = None
        self.gamma = None
        self.entropy_coef = None
        self.agent_info = agent_info
        self.feat_dim = self.agent_info["state_vector_size"]+1
        self.W_pi=None
        self.w_v=None
        self.prev_x = None
        self.prev_action = None
        self.rand_generator = np.random
        self.encoder=StateEncoderXDSAC(x_dimension=self.agent_info["state_vector_size"])
        self.obs_action_dict:Dict[int,int]={}

    def _V(self, x: np.ndarray) -> float:
        return float(np.dot(self.w_v, x))

    def _policy(self, x: np.ndarray) -> np.ndarray:
        logits = (x @ self.W_pi).astype(np.float32)  # (A,)
        return stable_softmax(logits)                # (A,)

    def _sample_action(self, probs: np.ndarray) -> int:
        return int(self.rand_generator.choice(self.num_actions, p=probs))

    @staticmethod
    def _entropy(probs: np.ndarray) -> float:
        # safe entropy: -sum p log p
        p = np.clip(probs, 1e-12, 1.0)
        return float( -1*np.sum(p * np.log(p)))

    @staticmethod
    def _grad_log_pi(x: np.ndarray, probs: np.ndarray, a: int) -> np.ndarray:
        """
        Gradient of log pi(a|s) wrt W_pi is:
          d/dW[:,k] log pi(a) = x * (1[a==k] - probs[k])
        Return matrix same shape as W_pi.
        """
        grad = -np.outer(x, probs).astype(np.float32)   # (feat_dim, A)
        grad[:, a] += x
        return grad

    @staticmethod
    def _grad_entropy(x: np.ndarray, probs: np.ndarray) -> np.ndarray:
        """
        Entropy bonus gradient wrt logits is (common A2C trick):
          dH/dlogits = - (diag(p) - p p^T) * (log p + 1)
        Then chain to W via outer(x, dH/dlogits).

        This is optional; if entropy_coef=0 it won't matter.
        """
        p = np.clip(probs, 1e-12, 1.0).astype(np.float32)
        u = (np.log(p) + 1.0).astype(np.float32)  # (A,)
        # J = diag(p) - p p^T
        j = np.diag(p) - np.outer(p, p)          # (A,A)
        dh_d_logits = -(j @ u).astype(np.float32) # (A,)
        return np.outer(x, dh_d_logits).astype(np.float32)



    def agent_init(self):
        self.num_actions = self.agent_info["num_actions"]
        self.alpha_pi = self.agent_info["alpha_pi"]
        self.alpha_v = self.agent_info["alpha_v"]
        self.gamma = self.agent_info["gamma"]
        self.entropy_coef = self.agent_info["entropy_coef"]
        self.rand_generator.default_rng(self.agent_info["seed"])
        self.W_pi = (0.01 * self.rand_generator.standard_normal((self.feat_dim, self.num_actions))).astype(np.float32)
        self.w_v = np.zeros((self.feat_dim,), dtype=np.float32)


    def agent_start(self, observation):
        x=self.encoder.encode_to_features(observation)
        s=self.encoder.encode(observation)
        probs = self._policy(x)
        a =self._sample_action(probs)
        self.prev_x = x
        self.prev_action = a
        self.obs_action_dict[s] = self.prev_action
        return a

    def agent_step(self, reward:float, observation:np.ndarray):
        assert self.prev_x is not None and self.prev_action is not None
        x =self.prev_x
        a= self.prev_action
        xp = self.encoder.encode_to_features(observation)
        s = self.encoder.encode(observation)
        # TD error
        v = self._V(x)
        vp = self._V(xp)
        delta = float(reward + self.gamma * vp - v)
        # ----- Critic update -----
        self.w_v += (self.alpha_v * delta) * x
        # ----- Actor update -----
        probs = self._policy(x)
        grad = self._grad_log_pi(x, probs, a)

        if self.entropy_coef != 0.0:
            grad += self.entropy_coef * self._grad_entropy(x, probs)

        self.W_pi += (self.alpha_pi * delta) * grad

        # sample next action from updated policy at s'
        probs_p = self._policy(xp)
        ap = self._sample_action(probs_p)

        self.prev_x = xp
        self.prev_action = ap
        self.obs_action_dict[s]=self.prev_action
        return ap

    def agent_end(self, reward:float):
        assert self.prev_x is not None and self.prev_action is not None
        x = self.prev_x
        a = self.prev_action
        v = self._V(x)
        delta = float(reward - v)  # terminal => no bootstrap
        # critic
        self.w_v += (self.alpha_v * delta) * x
        # actor
        probs = self._policy(x)
        grad = self._grad_log_pi(x, probs, a)
        if self.entropy_coef != 0.0:
            grad += self.entropy_coef * self._grad_entropy(x, probs)

        self.W_pi += (self.alpha_pi * delta) * grad
        self.prev_x = None
        self.prev_action = None

    def agent_cleanup(self)->None:
        self.prev_x = None
        self.prev_action = None

    def agent_message(self, message:str)->Any:
        if message == "get_shapes":
            return f"W_pi={self.W_pi.shape}, w_v={self.w_v.shape}"
        elif message == "get_w_pi":
            return self.W_pi
        elif message == "get_obs_action":
            return self.obs_action_dict
        else:
            return f"Unknown message:{message}"
