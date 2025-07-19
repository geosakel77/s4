import configparser


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
    }

    return config_values




