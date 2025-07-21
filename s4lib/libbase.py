import json,uvicorn,httpx, asyncio, uuid,openai,requests,re,tempfile
from distutils.command.upload import upload

from config.libconfig import read_config
from pyattck import Attck
from typing import  Any,List
from openai import OpenAI
from stix2 import FileSystemStore,Filter
from config.libconstants import MAP_TACTICS_TO_NAMES
from fastapi import FastAPI, Request
from typing import Dict
from contextlib import asynccontextmanager




def write_to_json(json_file,json_data):
    with open(json_file,'w') as outfile:
        json.dump(json_data,outfile)

def read_from_json(json_file):
    with open(json_file,'r') as infile:
        json_data = json.load(infile)
        return json_data



class APIServer:
    """
    Async HTTP server that exposes two endpoints:
      GET  /health    → {"status":"ok"}
      POST /echo      → {"received": <your JSON>}
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        self.host = host
        self.port = port
        self.app = FastAPI(title="Async Echo API")
        self._register_routes()

    def _register_routes(self) -> None:
        @self.app.get("/health")
        async def health() -> Dict[str, str]:
            return {"status": "ok"}

        @self.app.post("/echo")
        async def echo(req: Request) -> Dict[str, Any]:
            data = await req.json()
            return {"received": data}

    def run(self) -> None:
        """Block forever and serve HTTP until Ctrl‑C."""
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


class APIClient:
    """Async client for APIServer."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000") -> None:
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "APIClient":
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=10)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client:
            await self._client.aclose()

    async def health(self) -> Dict[str, Any]:
        """GET /health"""
        async with self._ensure_client() as cli:
            r = await cli.get("/health")
            r.raise_for_status()
            return r.json()

    async def echo(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /echo with arbitrary JSON"""
        async with self._ensure_client() as cli:
            r = await cli.post("/echo", json=payload)
            r.raise_for_status()
            return r.json()

    @asynccontextmanager
    async def _ensure_client(self):
        """Use existing client if inside __aenter__, else create temp one."""
        if self._client:  # already in a with‑block
            yield self._client
        else:             # standalone call
            async with httpx.AsyncClient(base_url=self.base_url, timeout=10) as cli:
                yield cli

class Agent:
    def __init__(self,agent_type,config_file='C:\\Users\\geosa\\PycharmProjects\\s4\\config\\config.ini'):
        self.uuid=uuid.uuid4()
        self.agent_type=agent_type
        self.config=read_config(config_file)
        self.server=APIServer()
        self.client=APIClient()


class OpenAIClient:
    def __init__(self, config):
        self.config=config
        self.client = OpenAI(api_key=self.config['openai_api_key'], organization=self.config['openai_organization_id'],
                             project=self.config['openai_project_id'])

    def call(self,message):
        response = self.client.responses.create(model=self.config['openai_model'],input=message)
        return response.output_text

    def call_openai(self, message):
        messages_list: list[dict[str, str | Any]] = [{
            "role": "user",
            "content": message
        }]
        response = self._call_run(messages_list)
        return response.choices[0].message['content']

    def _call_run(self, messages_list):
        return openai.ChatCompletion.create(model=self.config['openai_model'],messages=messages_list,temperature=0)
        #return self.client.ChatCompletion.create(messages=messages_list, model=self.config['openai_model'],
        #                                          temperature=0).choices[
        #    0].message.content


class AttackerAgent(Agent):
    def __init__(self, agent_type):
        super().__init__(agent_type=agent_type)
        self.actor=None
        self.actor_id=None
        self.actor_tactics=None
        self.actor_techniques=None
        self.actor_software=None
        self.kill_chain=MAP_TACTICS_TO_NAMES
        self.openai = OpenAIClient(self.config)

    def _generate_indicators(self):
        indicators={}
        actor_indicators=[]
        actor_external_references=self.actor['external_references']
        actor_external_references.pop(0)
        for actor_external_reference in actor_external_references:
            url=actor_external_reference['url']
            if url:
                indicator = self._generate_indicator(url)
                actor_indicators.append(indicator)
                indicators[self.actor_id]=actor_indicators

        for software in self.actor_software:
            software_dict=json.loads(software['object'])
            software_id=software_dict['id']
            software_indicators=[]
            software_external_references=software_dict['external_references']
            software_external_references.pop(0)
            for software_external_reference in software_external_references:
                if 'url' in software_external_reference.keys():
                    url=software_external_reference['url']
                    if url:
                        indicator=self._generate_indicator(url)
                        software_indicators.append(indicator)
                        indicators[software_id]=software_indicators
        return indicators

    def _generate_indicator(self,url:str):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            print(response.status_code)

            if url.endswith('pdf'):
                with tempfile.NamedTemporaryFile(suffix=".pdf",delete=False) as tmp:
                    tmp.write(response.content)
                    tmp_path=tmp.name
                    uploaded_file = self.openai.client.files.create(file=open(tmp_path,'rb'),purpose="assistants")
                    print(f"File ID:{uploaded_file.id}")
                    #TODO
                    assistant=self.openai.client.beta.assistants.create()
            else:
                pass


        except requests.exceptions.RequestException as e:
            print(e)

        return url


    def _extract_stix_indicators(self,response):
        extracted_json_text= self._extract_code_blocks(response)
        #try:
        #    data = json.loads(response)
        #    print("STIX bundle saved to apt17_iocs.json")
        #except json.JSONDecodeError:
        #    # If the assistant wrapped the JSON in markdown fences, strip them:
        #    cleaned = response.strip("```json\n").rstrip("```").strip()
        #    data = json.loads(cleaned)
        return extracted_json_text#data

    @staticmethod
    def _extract_code_blocks(markdown: str) -> List[str]:
        """
        Return every chunk of text found between matching pairs of ```
        (works whether or not a language tag follows the opening ```
        and is tolerant of leading/trailing whitespace).

        Example: >>> extract_code_blocks("Text ```python\nx=1```\nMore")
            ['python\nx=1']
        """
        pattern = r"```(?:[^\n]*\n)?(.*?)```"   # non‑greedy, DOTALL by default
        return re.findall(pattern, markdown, flags=re.DOTALL)



class AttackerAgentDA(Agent):

    def __init__(self,agent_type,custom=False):
        super().__init__(agent_type=agent_type)
        self.mitre_attack_da = FileSystemStore(self.config['mitre_enterprise_path'])
        self.custom=custom
        self.mitre_attack = Attck(nested_techniques=True, use_config=True,
                                  config_file_path=self.config['pyattck_path'],
                                  data_path=self.config['pyattck_data'],
                                  enterprise_attck_json=self.config['enterprise_attck_path'],
                                  generated_nist_json=self.config['generated_nist_path'],
                                  ics_attck_json=self.config['ics_attck_path'],
                                  mobile_attck_json=self.config['mobile_attck_path'],
                                  nist_controls_json=self.config['nist_controls_path'],
                                  pre_attck_json=self.config['pre_attck_path'])


    @staticmethod
    def remove_revoked_deprecated(stix_objects):
        """Remove any revoked or deprecated objects from queries made to the data source"""
        # Note we use .get() because the property may not be present in the JSON data. The default is False
        # if the property is not set.
        return list(
            filter(
                lambda x: x.get("x_mitre_deprecated", False) is False and x.get("revoked", False) is False,
                stix_objects
            )
        )

    def get_related(self,thesrc, src_type, rel_type, target_type, reverse=False):
        """build relationship mappings
           params:
             thesrc: MemoryStore to build relationship lookups for
             src_type: source type for the relationships, e.g "attack-pattern"
             rel_type: relationship type for the relationships, e.g "uses"
             target_type: target type for the relationship, e.g "intrusion-set"
             reverse: build reverse mapping of target to source
        """
        if not self.custom:
            thesrc = self.mitre_attack_da
        relationships = thesrc.query([
            Filter('type', '=', 'relationship'),
            Filter('relationship_type', '=', rel_type),
            Filter('revoked', '=', False),
        ])

        # See section below on "Removing revoked and deprecated objects"
        relationships = self.remove_revoked_deprecated(relationships)

        # stix_id => [ { relationship, related_object_id } for each related object ]
        id_to_related = {}

        # build the dict
        for relationship in relationships:
            if src_type in relationship.source_ref and target_type in relationship.target_ref:
                if (relationship.source_ref in id_to_related and not reverse) or (
                        relationship.target_ref in id_to_related and reverse):
                    # append to existing entry
                    if not reverse:
                        id_to_related[relationship.source_ref].append({
                            "relationship": relationship,
                            "id": relationship.target_ref
                        })
                    else:
                        id_to_related[relationship.target_ref].append({
                            "relationship": relationship,
                            "id": relationship.source_ref
                        })
                else:
                    # create a new entry
                    if not reverse:
                        id_to_related[relationship.source_ref] = [{
                            "relationship": relationship,
                            "id": relationship.target_ref
                        }]
                    else:
                        id_to_related[relationship.target_ref] = [{
                            "relationship": relationship,
                            "id": relationship.source_ref
                        }]
        # all objects of relevant type
        if not reverse:
            targets = thesrc.query([
                Filter('type', '=', target_type),
                Filter('revoked', '=', False)
            ])
        else:
            targets = thesrc.query([
                Filter('type', '=', src_type),
                Filter('revoked', '=', False)
            ])

        # build lookup of stixID to stix object
        id_to_target = {}

        for target in targets:
            id_to_target[target.id] = target

        # build final output mappings
        output = {}
        for stix_id in id_to_related:
            value = []
            for related in id_to_related[stix_id]:
                if not related["id"] in id_to_target:
                    continue  # targeting a revoked object
                value.append({
                    "object": id_to_target[related["id"]],
                    "relationship": related["relationship"]
                })
            output[stix_id] = value
        return output

    # software:group
    def software_used_by_groups(self,thesrc=None):
        """returns group_id => {software, relationship} for each software used by the group and each software used by campaigns attributed to the group."""
        # get all software used by groups
        if not self.custom:
            thesrc=self.mitre_attack_da
        tools_used_by_group = self.get_related(thesrc, "intrusion-set", "uses", "tool")
        malware_used_by_group = self.get_related(thesrc, "intrusion-set", "uses", "malware")
        software_used_by_group = {**tools_used_by_group,
                                  **malware_used_by_group}  # group_id -> [{software, relationship}]

        # get groups attributing to campaigns and all software used by campaigns
        software_used_by_campaign = self.get_related(thesrc, "campaign", "uses", "tool")
        malware_used_by_campaign = self.get_related(thesrc, "campaign", "uses", "malware")
        for id in malware_used_by_campaign:
            if id in software_used_by_campaign:
                software_used_by_campaign[id].extend(malware_used_by_campaign[id])
            else:
                software_used_by_campaign[id] = malware_used_by_campaign[id]
        campaigns_attributed_to_group = {
            "campaigns": self.get_related(thesrc, "campaign", "attributed-to", "intrusion-set", reverse=True),
            # group_id => {campaign, relationship}
            "software": software_used_by_campaign  # campaign_id => {software, relationship}
        }

        for group_id in campaigns_attributed_to_group["campaigns"]:
            software_used_by_campaigns = []
            # check if attributed campaign is using software
            for campaign in campaigns_attributed_to_group["campaigns"][group_id]:
                campaign_id = campaign["object"]["id"]
                if campaign_id in campaigns_attributed_to_group["software"]:
                    software_used_by_campaigns.extend(campaigns_attributed_to_group["software"][campaign_id])

            # update software used by group to include software used by a groups attributed campaign
            if group_id in software_used_by_group:
                software_used_by_group[group_id].extend(software_used_by_campaigns)
            else:
                software_used_by_group[group_id] = software_used_by_campaigns
        return software_used_by_group

    def groups_using_software(self,thesrc=None):
        """returns software_id => {group, relationship} for each group using the software and each software used by attributed campaigns."""
        # get all groups using software
        if not self.custom:
            thesrc=self.mitre_attack_da
        groups_using_tool = self.get_related(thesrc, "intrusion-set", "uses", "tool", reverse=True)
        groups_using_malware = self.get_related(thesrc, "intrusion-set", "uses", "malware", reverse=True)
        groups_using_software = {**groups_using_tool, **groups_using_malware}  # software_id => {group, relationship}

        # get campaigns attributed to groups and all campaigns using software
        campaigns_using_software = self.get_related(thesrc, "campaign", "uses", "tool", reverse=True)
        campaigns_using_malware = self.get_related(thesrc, "campaign", "uses", "malware", reverse=True)
        for id in campaigns_using_malware:
            if id in campaigns_using_software:
                campaigns_using_software[id].extend(campaigns_using_malware[id])
            else:
                campaigns_using_software[id] = campaigns_using_malware[id]
        groups_attributing_to_campaigns = {
            "campaigns": campaigns_using_software,  # software_id => {campaign, relationship}
            "groups": self.get_related(thesrc, "campaign", "attributed-to", "intrusion-set")
            # campaign_id => {group, relationship}
        }

        for software_id in groups_attributing_to_campaigns["campaigns"]:
            groups_attributed_to_campaigns = []
            # check if campaign is attributed to group
            for campaign in groups_attributing_to_campaigns["campaigns"][software_id]:
                campaign_id = campaign["object"]["id"]
                if campaign_id in groups_attributing_to_campaigns["groups"]:
                    groups_attributed_to_campaigns.extend(groups_attributing_to_campaigns["groups"][campaign_id])

            # update groups using software to include software used by a groups attributed campaign
            if software_id in groups_using_software:
                groups_using_software[software_id].extend(groups_attributed_to_campaigns)
            else:
                groups_using_software[software_id] = groups_attributed_to_campaigns
        return groups_using_software

    # technique:group
    def techniques_used_by_groups(self,thesrc=None):
        """returns group_id => {technique, relationship} for each technique used by the group and each
           technique used by campaigns attributed to the group."""
        # get all techniques used by groups
        if not self.custom:
            thesrc= self.mitre_attack_da
        techniques_used_by_groups = self.get_related(thesrc, "intrusion-set", "uses",
                                                "attack-pattern")  # group_id => {technique, relationship}

        # get groups attributing to campaigns and all techniques used by campaigns
        campaigns_attributed_to_group = {
            "campaigns": self.get_related(thesrc, "campaign", "attributed-to", "intrusion-set", reverse=True),
            # group_id => {campaign, relationship}
            "techniques": self.get_related(thesrc, "campaign", "uses", "attack-pattern")
            # campaign_id => {technique, relationship}
        }

        for group_id in campaigns_attributed_to_group["campaigns"]:
            techniques_used_by_campaigns = []
            # check if attributed campaign is using technique
            for campaign in campaigns_attributed_to_group["campaigns"][group_id]:
                campaign_id = campaign["object"]["id"]
                if campaign_id in campaigns_attributed_to_group["techniques"]:
                    techniques_used_by_campaigns.extend(campaigns_attributed_to_group["techniques"][campaign_id])

            # update techniques used by groups to include techniques used by a groups attributed campaign
            if group_id in techniques_used_by_groups:
                techniques_used_by_groups[group_id].extend(techniques_used_by_campaigns)
            else:
                techniques_used_by_groups[group_id] = techniques_used_by_campaigns
        return techniques_used_by_groups

    def groups_using_technique(self,thesrc=None):
        """returns technique_id => {group, relationship} for each group using the technique and each campaign attributed to groups using the technique."""
        # get all groups using techniques
        if not self.custom:
            thesrc = self.mitre_attack_da
        groups_using_techniques = self.get_related(thesrc, "intrusion-set", "uses", "attack-pattern",
                                              reverse=True)  # technique_id => {group, relationship}

        # get campaigns attributed to groups and all campaigns using techniques
        groups_attributing_to_campaigns = {
            "campaigns": self.get_related(thesrc, "campaign", "uses", "attack-pattern", reverse=True),
            # technique_id => {campaign, relationship}
            "groups": self.get_related(thesrc, "campaign", "attributed-to", "intrusion-set")
            # campaign_id => {group, relationship}
        }

        for technique_id in groups_attributing_to_campaigns["campaigns"]:
            campaigns_attributed_to_group = []
            # check if campaign is attributed to group
            for campaign in groups_attributing_to_campaigns["campaigns"][technique_id]:
                campaign_id = campaign["object"]["id"]
                if campaign_id in groups_attributing_to_campaigns["groups"]:
                    campaigns_attributed_to_group.extend(groups_attributing_to_campaigns["groups"][campaign_id])

            # update groups using techniques to include techniques used by a groups attributed campaign
            if technique_id in groups_using_techniques:
                groups_using_techniques[technique_id].extend(campaigns_attributed_to_group)
            else:
                groups_using_techniques[technique_id] = campaigns_attributed_to_group
        return groups_using_techniques


    # technique:software
    def techniques_used_by_software(self,thesrc=None):
        """return software_id => {technique, relationship} for each technique used by the software."""
        if not self.custom:
            thesrc = self.mitre_attack_da
        techniques_by_tool = self.get_related(thesrc, "tool", "uses", "attack-pattern")
        techniques_by_malware = self.get_related(thesrc, "malware", "uses", "attack-pattern")
        return {**techniques_by_tool, **techniques_by_malware}

    def software_using_technique(self,thesrc=None):
        """return technique_id  => {software, relationship} for each software using the technique."""
        if not self.custom:
            thesrc = self.mitre_attack_da
        tools_by_technique_id = self.get_related(thesrc, "tool", "uses", "attack-pattern", reverse=True)
        malware_by_technique_id = self.get_related(thesrc, "malware", "uses", "attack-pattern", reverse=True)
        return {**tools_by_technique_id, **malware_by_technique_id}

    # technique:mitigation
    def mitigation_mitigates_techniques(self,thesrc=None):
        """return mitigation_id => {technique, relationship} for each technique mitigated by the mitigation."""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "course-of-action", "mitigates", "attack-pattern", reverse=False)

    def technique_mitigated_by_mitigations(self,thesrc=None):
        """return technique_id => {mitigation, relationship} for each mitigation of the technique."""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "course-of-action", "mitigates", "attack-pattern", reverse=True)

    # technique:sub-technique
    def subtechniques_of(self,thesrc=None):
        """return technique_id => {subtechnique, relationship} for each subtechnique of the technique."""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "attack-pattern", "subtechnique-of", "attack-pattern", reverse=True)

    def parent_technique_of(self,thesrc=None):
        """return subtechnique_id => {technique, relationship} describing the parent technique of the subtechnique"""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "attack-pattern", "subtechnique-of", "attack-pattern")[0]

    # technique:data-component
    def datacomponent_detects_techniques(self,thesrc=None):
        """return datacomponent_id => {technique, relationship} describing the detections of each data component"""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "x-mitre-data-component", "detects", "attack-pattern")

    def technique_detected_by_datacomponents(self,thesrc=None):
        """return technique_id => {datacomponent, relationship} describing the data components that can detect the technique"""
        if not self.custom:
            thesrc = self.mitre_attack_da
        return self.get_related(thesrc, "x-mitre-data-component", "detects", "attack-pattern", reverse=True)

class MITREATTCKConfig(AttackerAgentDA):

    def __init__(self,agent_type="MITREATTCK"):
        super().__init__(agent_type=agent_type)
        self.openai_client = OpenAIClient(config=self.config)
        self.actors= self._get_actors()
        self.controls= self._get_controls()
        self.malwares=self._get_malwares()
        self.mitigations= self._get_mitigations()
        self.tactics= self._get_tactics()
        self.techniques= self._get_techniques()
        self.tools= self._get_tools()

    def _get_actors(self):
        actors ={}
        for actor in self.mitre_attack.enterprise.actors:
            ext_ref_serialized=[]
            for ext_ref in actor.external_references:
                ext_ref_serialized.append({'source_name':ext_ref.source_name,'url':ext_ref.url,'external_id':ext_ref.external_id,'description':ext_ref.description})
            serialized_actor = {'id':actor.id,
                                'name':actor.name,
                                'created':actor.created,
                                'modified':actor.modified,
                                'x_mitre_version':actor.x_mitre_version,
                                'type':actor.type,
                                'aliases':actor.aliases,
                                'x_mitre_contributors':actor.x_mitre_contributors,
                                'revoked':actor.revoked,
                                'description':actor.description,
                                'x_mitre_modified_by_ref':actor.x_mitre_modified_by_ref,
                                'x_mitre_deprecated':actor.x_mitre_deprecated,
                                'x_mitre_attack_spec_version':actor.x_mitre_attack_spec_version,
                                'created_by_ref':actor.created_by_ref,
                                'x_mitre_domains':actor.x_mitre_domains,
                                'object_marking_refs':actor.object_marking_refs,
                                'external_references':ext_ref_serialized,
                                'names':actor.names,
                                'external_tools':actor.external_tools,
                                'country':actor.country,
                                'operations':actor.operations,
                                'links':actor.links,
                                'targets':actor.targets,
                                'external_description':actor.external_description,
                                'attck_id':actor.attck_id,
                                'comment':actor.comment}
            actors[actor.id]=serialized_actor
        return actors

    def _get_controls(self):
        controls ={}
        for control in self.mitre_attack.enterprise.controls:
            controls[control.id]={'name':control.name,'x_mitre_family':control.x_mitre_family,"control_id":control.external_references[0].external_id}
        return controls

    def _get_malwares(self):
        malwares={}
        for malware in self.mitre_attack.enterprise.malwares:
            malwares[malware.id]={'name':malware.name,"malware_id":malware.external_references[0].external_id,'x_mitre_platforms':malware.x_mitre_platforms}
        return malwares

    def _get_mitigations(self):
        mitigations={}
        for mitigation in self.mitre_attack.enterprise.mitigations:
            if not mitigation.x_mitre_deprecated:
                mitigations[mitigation.id]={"name":mitigation.name,"mitigation_id":mitigation.external_references[0].external_id}
        return mitigations

    def _get_tactics(self):
        tactics ={}
        for tactic in self.mitre_attack.enterprise.tactics:
            tactics[tactic.id]={'name':tactic.name,"tactic_id":tactic.external_references[0].external_id}
        return tactics

    def _get_techniques(self):
        techniques ={}
        for technique in self.mitre_attack.enterprise.techniques:
            kill_chain_phases=[]
            for kill_chain in technique.kill_chain_phases:
                kill_chain_phases.append(kill_chain.phase_name)
            techniques[technique.id]={'name':technique.name,'x_mitre_is_subtechnique':technique.x_mitre_is_subtechnique,'technique_id':technique.technique_id,'x_mitre_platforms':technique.x_mitre_platforms,'kill_chain_phases':kill_chain_phases}
        return techniques

    def _get_tools(self):
        tools ={}
        for tool in self.mitre_attack.enterprise.tools:
            tools[tool.id]={'name':tool.name,"tool_id":tool.external_references[0].external_id,'x_mitre_platforms': tool.x_mitre_platforms}
        return tools

    @staticmethod
    def get_data_serialized(data):
        serialized_data={}
        for key in data.keys():
            list_of_dict=data[key]
            serialized_list_of_dicts=[]
            for dict_obj_rel in list_of_dict:
                new_entry= {'object': dict_obj_rel['object'].serialize(),
                            'relationship': dict_obj_rel['relationship'].serialize()}
                serialized_list_of_dicts.append(new_entry)
            serialized_data[key]=serialized_list_of_dicts
        return serialized_data



