import os,json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH


if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    file_paths = os.listdir(config['experiments_data_path'])
    indicators=[]
    actors=[]
    for file_path in file_paths:
        with open(os.path.join("../experiments_data", file_path), 'r', encoding='utf-8') as f:
            data = json.load(f)
            indicators.append(data['indicators'])
            actors.append(data['actor']['name'])
    print(actors)