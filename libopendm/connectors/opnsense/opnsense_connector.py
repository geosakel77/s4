from libopendm.connectors.opnsense.connection import CONNECTION_DATA
import requests
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import uuid

HOST = "0.0.0.0"
PORT = 6500
DIRECTORY_NAME="shared_rules"
DIRECTORY_PATH=Path(DIRECTORY_NAME)

class FileServer(SimpleHTTPRequestHandler):
    def __init__(self, *args,**kwargs):
        super().__init__(*args, directory=str(DIRECTORY_PATH), **kwargs)

def ruleset_sharing_server():
    ThreadingHTTPServer((HOST, PORT), FileServer).serve_forever()


class OPNSenseConnector:
    def __init__(self,connection_data=CONNECTION_DATA,host=HOST,port=PORT,dm_agent_uuid=None):
        self.api_key = connection_data["key"]
        self.api_secret = connection_data["secret"]
        self.url = connection_data["url"]
        self.certificate = connection_data["certificate"]
        print(DIRECTORY_PATH.absolute())
        if dm_agent_uuid is None:
            self.dm_agent_uuid = str(uuid.uuid4())
        else:
            self.dm_agent_uuid = dm_agent_uuid
        DIRECTORY_PATH.mkdir(exist_ok=True)

    def get_fw_ids_status(self):
        url = self.url + "ids/service/status"
        r=requests.get(url,verify=self.certificate,auth=(self.api_key,self.api_secret))
        status = None
        if r.status_code == 200:
            response = r.json()
            print(f"IDS status: {response['status']}")
            status = response['status']
        return status

    def get_fw_ids_settings(self):
        url = self.url + "ids/settings/get"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        ids_settings = {}
        if r.status_code == 200:
            response = r.json()
            print(response['ids']['general'].keys())
            ids_settings["enabled"]=response['ids']['general']["enabled"]
            ids_settings["mode"]=response['ids']['general']["mode"]
            ids_settings["interfaces"]=response['ids']['general']["interfaces"]
            ids_settings["syslog"]=response['ids']['general']["syslog"]
            ids_settings["verbosity"]=response['ids']['general']["verbosity"]
            print("Firewall IDS Settings:")
            for key, value in ids_settings.items():
                print(f"{key}: {value}")
        else:
            print(f"Firewall response status: {r.status_code}")
        return ids_settings


    def get_fw_ids_rulesets(self):
        url = self.url + "ids/settings/list_rulesets"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        rulesets = []
        if r.status_code == 200:
            response = r.json()
            for ruleset in response['rows']:
                rulesets.append({"description":ruleset['description'],
                 "enabled":ruleset['enabled'],})
            for ruleset in rulesets:
                print(f"{ruleset['description']} - Enabled: {ruleset['enabled']}")
        else:
            print(f"Firewall response status: {r.status_code}")
        return rulesets

    def get_fw_ids_user_rules(self):
        url = self.url + "ids/settings/search_user_rule"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        rules = []
        if r.status_code == 200:
            response = r.json()
            for rule in response['rows']:
                rules.append(rule)
            for rule in rules:
                print(f"{rule['uuid']} - {rule['description']} - Enabled: {rule['enabled']}")
        else:
            print(f"Firewall response status: {r.status_code}")
        return rules

    def search_fw_ids_policy(self):
        url = self.url + "ids/settings/search_policy"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        data=None
        if r.status_code == 200:
            response = r.json()
            print(response)
            data=response
        else:
            print(f"Firewall response status: {r.status_code}")
        return data

    def get_fw_ids_policy(self):
        url = self.url + "ids/settings/get_policy"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        data=None
        if r.status_code == 200:
            response = r.json()
            print(response)
            data=response
        else:
            print(f"Firewall response status: {r.status_code}")
        return data

    def add_fw_ids_policy(self,uuid=None,enabled=None,prio='2',action=None,n_action=None,ruleset=None,n_ruleset=None,content=None,new_action=None,n_new_action=None,description=None):
        payload = {"enabled": enabled or '1', "prio": prio or '0',
                   "action": action or 'alert', "%action": n_action or 'Alert', "rulesets": ruleset or '',
                   "%rulesets": n_ruleset or '', "content": content or 'DM Agent Content',
                   "new_action": new_action or 'alert', "%new_action": n_new_action or 'Alert',
                   "description": description or 'DM Agent Policy'}
        print(payload)
        url = self.url + "ids/settings/add_policy"
        policy_payload = {"policy":payload}
        r = requests.post(url,data=policy_payload,verify=self.certificate, auth=(self.api_key, self.api_secret))
        data = None
        if r.status_code == 200:
            response = r.json()
            print(response)
            data = response
        else:
            print(f"Firewall response status: {r.status_code}")
        return data

    def get_fw_ids_policy_rules(self):

        url = self.url + "ids/settings/get_policy_rule"
        r = requests.get(url, verify=self.certificate, auth=(self.api_key, self.api_secret))
        rules = []
        if r.status_code == 200:
            response = r.json()
            print(response)

        else:
            print(f"Firewall response status: {r.status_code}")
        return rules
    def create_suricata_ids_rule(self,payload):
        pass

    def update_fw_ids_ruleset(self):
        pass