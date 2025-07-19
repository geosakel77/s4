import configparser

from tests.conftest import mitre_attack_data_enterprise


def read_config(filepath="config.ini"):
    # Create a ConfigParser object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read(filepath)

    # Access values from the configuration file
    debug_mode = config.getboolean('general', 'debug')
    log_level = config.get('general', 'log_level')
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

    openai_api_key = config.get('openai', 'openai_api_key')
    openai_organization_id = config.get('openai', 'organization_id')
    openai_project_id = config.get('openai', 'project_id')
    openai_model = config.get('openai', 'model')

    # Return a dictionary with the retrieved values
    config_values = {
        'debug_mode': debug_mode,
        'log_level': log_level,
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
        'openai_api_key': openai_api_key,
        'openai_organization_id': openai_organization_id,
        'openai_project_id': openai_project_id,
        'openai_model': openai_model,
    }

    return config_values




