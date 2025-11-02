import os,json
from s4config.libconfig import read_config
from s4config.libconstants import CONFIG_PATH
from s4lib.libbase import read_from_json


if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    data = read_from_json(config['cti_data_pool'])
    pattern_types=[]
    test_types=[]

    for key in data.keys():
        if data[key]['type']=='indicator':
            if data[key]['pattern'].startswith("["):
                if "OR" in data[key]['pattern']:
                    for p in data[key]['pattern'].replace('[','').replace(']','').split("OR"):
                        val1=p.split("=")[0].split("MATCHES")[0].split("IN")[0].replace('(','').replace("'",'').replace('"','').strip()
                        if ":" in val1 and "http" not in val1:
                            pattern_types.append(val1)
                elif "IN" in data[key]['pattern']:
                    pattern_types.append(data[key]['pattern'].split("IN")[0].split("=")[0].replace('[','').replace(']','').replace("'",'').replace('"','').strip())
                else:
                    val1 = data[key]['pattern'].replace('[','').replace(']','').split('=')[0].replace("'",'').replace('"','').split("MATCHES")[0].split("LIKE")[0].strip()
                    pattern_types.append(val1)
        elif data[key]['type']=='vulnerability':
            pattern_types.append(data[key]['type'])

    ext=['network-traffic:user_agent', 'windows-registry-key:key', 'vulnerability:name', 'directory:path', 'x-crypto-address:value', 'malware:name', 'email-addr:value', 'network-traffic:dst_port', 'rule', 'network-traffic:extensions', 'process:mutexes[*]', 'file:path', 'x509-certificate:serial_number', 'url:value', 'file:hashes', 'file:parent_directory_ref', 'process:name', 'artifact:payload_bin', 'domain-name:value', 'process:command_line', 'ipv4-addr:value', 'file:name', 'mutex:name']
    pattern_types.extend(ext)

    print(set(pattern_types))
    print(len(set(pattern_types)))
    print(len(set(test_types)))
    print(set(test_types))