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
import configparser


def read_config(filepath="config.ini"):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(filepath)

    # Access values from the configuration file
    debug_mode = config.getboolean('general', 'debug')
    log_level = config.get('general', 'log_level')
    wkhtmltopdf_path = config.get('general', 'wkhtmltopdf_path')
    images_path = config.get('general', 'images_path')
    logs_dir=config.get('general', 'logs_dir')
    pyattck_path = config.get('ta', 'pyattck_path')
    pyattck_data=config.get('ta', 'pyattck_data')
    enterprise_attck_path=config.get('ta', 'enterprise_attck_path')
    generated_nist_path = config.get('ta', 'generated_nist_path')
    ics_attck_path = config.get('ta', 'ics_attck_path')
    mobile_attck_path = config.get('ta', 'mobile_attck_path')
    nist_controls_path = config.get('ta', 'nist_controls_path')
    pre_attck_path=config.get('ta', 'pre_attck_path')
    actors_path = config.get('ta', 'actors_path')
    tactics_path = config.get('ta', 'tactics_path')
    malwares_path = config.get('ta', 'malwares_path')
    controls_path = config.get('ta', 'controls_path')
    mitigations_path = config.get('ta', 'mitigations_path')
    tools_path = config.get('ta', 'tools_path')
    techniques_path = config.get('ta', 'techniques_path')
    mitre_enterprise_path = config.get('ta', 'mitre_enterprise_path')
    software_used_by_groups = config.get('ta', 'software_used_by_groups')
    techniques_used_by_groups = config.get('ta', 'techniques_used_by_groups')
    software_using_technique = config.get('ta', 'software_using_technique')
    ta_plan_threshold=config.get('ta', 'ta_plan_threshold')
    ta_actor_max_plans = config.get('ta', 'ta_actor_max_plans')
    openai_api_key = config.get('openai', 'openai_api_key')
    openai_organization_id = config.get('openai', 'organization_id')
    openai_project_id = config.get('openai', 'project_id')
    openai_model = config.get('openai', 'model')
    experiments_data_path = config.get('experiments', 'experiments_data_path')
    coordinator_port=config.get('experiments', 'coordinator_port')
    coordinator_host=config.get('experiments', 'coordinator_host')
    generic_host=config.get('experiments', 'generic_host')
    templates_path = config.get('experiments', 'templates_path')
    experiment_results_path=config.get('experiments', 'experiment_results_path')
    static_path = config.get('experiments', 'static_path')
    heartbeat_rate=config.getint('experiments', 'heartbeat_rate')
    time_steps=config.getint('experiments', 'time_steps')
    max_number_of_assets=config.getint('experiments', 'max_number_of_assets')
    step_duration=config.getint('experiments', 'step_duration')
    d3fend_path=config.get('dm', 'd3fend_path')
    l1=config.getfloat('dm', 'l1')
    l2=config.getfloat('dm', 'l2')
    l3=config.getfloat('dm', 'l3')
    applicability_reward=config.getfloat('dm', 'applicability_reward')
    hit_reward=config.getfloat('dm', 'hit_reward')
    hardening_threshold=config.getfloat('dm', 'hardening_threshold')
    harden_q_steps=config.getint('dm', 'harden_q_steps')
    pulsedive_key=config.get('src', 'pulsedive_key')
    discovery_url=config.get('src', 'discovery_url')
    indicators_collection=config.get('src', 'indicators_collection')
    threat_collection=config.get('src', 'threat_collection')
    pulse_cti_store_data=config.get('src', 'pulse_cti_store_data')
    otx_cti_store_data = config.get('src', 'otx_cti_store_data')
    otx_discovery = config.get('src', 'otx_discovery')
    otx_key = config.get('src', 'otx_key')
    electiciq_cti_store_data = config.get('src', 'electiciq_cti_store_data')
    electiciq_discovery = config.get('src', 'electiciq_discovery')
    cti_data_pool =config.get('src', 'cti_data_pool')
    rl_server_port=config.getint('rl', 'rl_server_port')
    rl_server_ip=config.get('rl', 'rl_server_ip')
    worker_index=config.getint('rl', 'worker_index')
    rl_config_path=config.get('rl', 'rl_config_path')
    rl_config_path_simple=config.get('rl', 'rl_config_path_simple')
    rl_num_episodes=config.getint('rl', 'rl_num_episodes')
    rl_agent_type=config.getint('rl', 'rl_agent_type')
    validation_data_dir=config.get('validation', 'validation_data_dir')
    validation_data_path=config.get('validation', 'validation_data_path')
    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'wkhtmltopdf_path': wkhtmltopdf_path,
        'images_path': images_path,
        'logs_dir': logs_dir,
        'pyattck_path': pyattck_path,
        'pyattck_data': pyattck_data,
        'enterprise_attck_path': enterprise_attck_path,
        'generated_nist_path': generated_nist_path,
        'ics_attck_path': ics_attck_path,
        'mobile_attck_path': mobile_attck_path,
        'nist_controls_path': nist_controls_path,
        'pre_attck_path': pre_attck_path,
        'actors_path': actors_path,
        'tactics_path': tactics_path,
        'malwares_path': malwares_path,
        'controls_path': controls_path,
        'mitigations_path': mitigations_path,
        'tools_path': tools_path,
        'techniques_path': techniques_path,
        'mitre_enterprise_path': mitre_enterprise_path,
        'software_used_by_groups': software_used_by_groups,
        'techniques_used_by_groups': techniques_used_by_groups,
        'software_using_technique': software_using_technique,
        'openai_api_key': openai_api_key,
        'openai_organization_id': openai_organization_id,
        'openai_project_id': openai_project_id,
        'openai_model': openai_model,
        'experiments_data_path': experiments_data_path,
        'experiment_results_path': experiment_results_path,
        'ta_plan_threshold': ta_plan_threshold,
        'ta_actor_max_plans': ta_actor_max_plans,
        'coordinator_port': coordinator_port,
        'coordinator_host': coordinator_host,
        'generic_host': generic_host,
        'templates_path': templates_path,
        'static_path': static_path,
        'heartbeat_rate': heartbeat_rate,
        'time_steps': time_steps,
        'max_number_of_assets': max_number_of_assets,
        'step_duration': step_duration,
        'd3fend_path': d3fend_path,
        'l1': l1,
        'l2': l2,
        'l3': l3,
        'applicability_reward': applicability_reward,
        'hit_reward': hit_reward,
        'hardening_threshold': hardening_threshold,
        'harden_q_steps': harden_q_steps,
        'pulsedive_key': pulsedive_key,
        'discovery_url': discovery_url,
        'indicators_collection': indicators_collection,
        'threat_collection': threat_collection,
        'pulse_cti_store_data':pulse_cti_store_data,
        'otx_cti_store_data': otx_cti_store_data,
        'otx_discovery': otx_discovery,
        'otx_key': otx_key,
        'electiciq_cti_store_data': electiciq_cti_store_data,
        'electiciq_discovery': electiciq_discovery,
        'cti_data_pool': cti_data_pool,
        'rl_server_port': rl_server_port,
        'rl_server_ip': rl_server_ip,
        'worker_index': worker_index,
        'rl_config_path': rl_config_path,
        'rl_config_path_simple': rl_config_path_simple,
        'rl_num_episodes': rl_num_episodes,
        'rl_agent_type': rl_agent_type,
        'validation_data_path': validation_data_path,
        'validation_data_dir': validation_data_dir,
    }

    return config_values





