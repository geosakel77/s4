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
    static_path = config.get('experiments', 'static_path')
    heartbeat_rate=config.getint('experiments', 'heartbeat_rate')
    time_steps=config.getint('experiments', 'time_steps')
    max_number_of_assets=config.getint('experiments', 'max_number_of_assets')
    step_duration=config.getint('experiments', 'step_duration')
    d3fend_path=config.get('dm', 'd3fend_path')
    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
        'wkhtmltopdf_path': wkhtmltopdf_path,
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
    }

    return config_values




