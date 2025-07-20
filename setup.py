from s4lib.libbase import write_to_json,read_from_json
from s4lib.libbase import MITREATTCKConfig
from pprint import pprint

def run():
    print("Preparing Configuration for S4")
    mitreattackconfig = MITREATTCKConfig()
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

    print("... end of S4 setup")


if __name__=='__main__':
    run()


