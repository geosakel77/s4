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

from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config
from s4lib.libagcti import record_encoder
from s4lib.libsrc import CTISRC
import uuid

def records_creator_test():
        config = read_config(CONFIG_PATH)
        ctisrc = CTISRC(agent_uuid=uuid.uuid4(), config=config)
        record=ctisrc.shared_cti_product
        record_encoder(record)



if __name__ == '__main__':
    records_creator_test()