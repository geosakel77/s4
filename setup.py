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

from s4lib.libbase import write_to_json
from s4lib.libbase import MITREATTCKConfig,MITRED3FENDConfig,CTISourceConfig
from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config

def attack_run(config):
    print("Preparing Attackers Configuration for S4")
    mitreattackconfig = MITREATTCKConfig(config)
    print("...extracting and writing controls")
    write_to_json(mitreattackconfig.config['actors_path'],mitreattackconfig.actors)
    print("...extracting and writing controls")
    write_to_json(mitreattackconfig.config['controls_path'],mitreattackconfig.controls)
    print("...extracting and writing malwares")
    write_to_json(mitreattackconfig.config['malwares_path'], mitreattackconfig.malwares)
    print("...extracting and writing mitigations")
    write_to_json(mitreattackconfig.config['mitigations_path'],mitreattackconfig.mitigations)
    print("...extracting and writing tactics")
    write_to_json(mitreattackconfig.config['tactics_path'], mitreattackconfig.tactics)
    print("...extracting and writing techniques")
    write_to_json(mitreattackconfig.config['techniques_path'],mitreattackconfig.techniques)
    print("...extracting and writing tools")
    write_to_json(mitreattackconfig.config['tools_path'],mitreattackconfig.tools)
    print("...extracting and writing software used by groups")
    write_to_json(mitreattackconfig.config['software_used_by_groups'],mitreattackconfig.get_data_serialized(mitreattackconfig.software_used_by_groups()))
    print("...extracting and writing techniques used by groups")
    write_to_json(mitreattackconfig.config['techniques_used_by_groups'],mitreattackconfig.get_data_serialized(mitreattackconfig.techniques_used_by_groups()))
    print("...extracting and writing software using technique")
    write_to_json(mitreattackconfig.config['software_using_technique'],mitreattackconfig.get_data_serialized(mitreattackconfig.software_using_technique()))

    print("... end of S4 Attackers setup")

def defend_run(config):
    print("Preparing Defenders Configuration for S4")
    defenderconfig = MITRED3FENDConfig(config)
    for key,value in defenderconfig.d3fend_kb['tactics'].items():
        tech_c=defenderconfig.d3fend_kb['techniques_categories'][key]
        print(f"---{value}")
        for key1,value1 in tech_c.items():
            print(f"-----{value1}")
            tech=defenderconfig.d3fend_kb['techniques'][key1]
            for key2,value2 in tech.items():
                print(f"--------{value2}")

    print("...extracting and writing controls")


def cti_run(config):
    print("Preparing CTI Source Configuration for S4")
    ctisourceconfig = CTISourceConfig(config)
    ctisourceconfig.get_pulsedive_data()
    ctisourceconfig.get_otx_data()
    ctisourceconfig.get_electiciq_data()
    ctisourceconfig.create_cti_source_pool()
    print("...extracting and writing cti data")

if __name__=='__main__':
    print("Preparing Configuration for S4")
    config = read_config(CONFIG_PATH)
    attack_run(config)
    defend_run(config)
    cti_run(config)
    print("... end of S4 setup")


