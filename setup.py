from lib.libbase import write_to_json,read_from_json
from lib.libbase import MITREATTCKConfig
if __name__=='__main__':
    print("Preparing Configuration for S4")
    mitreattackconfig = MITREATTCKConfig()
    write_to_json(mitreattackconfig.config['actors_path'],mitreattackconfig.actors)
    data = read_from_json(mitreattackconfig.config['actors_path'])
    print(data)