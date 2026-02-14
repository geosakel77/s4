""""
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
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, Any, Optional

class StateEncoderXD:
    """Maps an x-D bit vector to a discrete state key"""

    def __init__(self,x_dimension=49):
        self.x =x_dimension

    def encode(self,state_x: np.ndarray) -> int:
        """
        state_x: array-like shape (x,), values in {0,1}
        Returns an int in [0, 2^x - 1]
        """
        b = np.asarray(state_x, dtype=np.uint8).reshape(self.x, )
        # dot with powers of 2
        powers = (1 << np.arange(self.x, dtype=np.uint32))
        return int((b * powers).sum())

    def validate_bits_x(self,state_x: np.ndarray) -> None:
        b = np.asarray(state_x).reshape(self.x, )
        if not np.all((b == 0) | (b == 1)):
            raise ValueError(f"State must be a {state_x}-D binary vector containing only 0/1.")

