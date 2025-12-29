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

import json, openai,requests,re,tempfile,pdfkit,os,time,random,nvdlib
from io import BytesIO
from cabby import create_client

from taxii2client.v21 import Server,as_pages
from requests.auth import HTTPBasicAuth
from rdflib.plugins.sparql import prepareQuery
from pyattck import Attck
from typing import  Any,List
from openai import OpenAI
from stix2 import FileSystemStore,Filter,parse

from s4config.libconstants import MAP_TACTICS_TO_NAMES
from colorama import Fore,Style
from rdflib import Graph,Namespace, URIRef

def write_to_json(json_file,json_data):
    with open(json_file,'w') as outfile:
        json.dump(json_data,outfile)

def read_from_json(json_file):
    with open(json_file,'r',encoding="utf-8") as infile:
        json_data = json.load(infile)
        return json_data

def validate_schema(data, schema):
    if not isinstance(data, dict):
        return False
    for key, expected_type in schema.items():
        if key not in data or not isinstance(data[key], expected_type):
            return False
    return True

def determine_color_impact(data):
    color= None
    if data[1]==1:
        color= Fore.GREEN
    elif data[1]==2:
        color=Fore.YELLOW
    elif data[1]==3:
        color=Fore.RED
    return color

def determine_color_classification(classification_key):
    color= None
    if classification_key==1:
        color= Fore.BLUE
    elif classification_key==2:
        color=Fore.CYAN
    elif classification_key==3:
        color=Fore.GREEN
    elif classification_key==4:
        color=Fore.YELLOW
    elif classification_key==5:
        color =Fore.RED
    return color

def print_security_characteristics(security_category,confidentiality,integrity,availability,classification,classification_key):
        c=determine_color_impact(security_category[0])
        ic=determine_color_impact(security_category[1])
        a=determine_color_impact(security_category[2])
        cls = determine_color_classification(classification_key)
        print(f"{c}Confidentiality: {confidentiality}{Style.RESET_ALL} - {ic}Integrity: {integrity}{Style.RESET_ALL} - {a}Availability: {availability}{Style.RESET_ALL} - {cls}Classification: {classification}{Style.RESET_ALL} ")

class Agent:
    def __init__(self,agent_uuid,agent_type,config):
        self.uuid=agent_uuid
        self.agent_type=agent_type
        self.config=config
        self.connection_data_ta = {}
        self.connection_data_dm = {}
        self.connection_data_cti = {}
        self.connection_data_is = {}
        self.connection_data_src = {}
        self.registered_agents=[]
        self.client=None
        self.clock:int=0

    def update_connection_data(self,data):
        try:
            self.connection_data_ta = data["TA"]
            self.connection_data_dm = data["DM"]
            self.connection_data_cti = data["CTI"]
            self.connection_data_is = data["IS"]
            self.connection_data_src = data["SRC"]
            self.registered_agents = data["RA"]
            update_status = {"status":"Success"}
        except KeyError as e:
            print(e)
            update_status = {"status":"Error"}
        return update_status

    async def update_time(self,data):
        try:
            self.clock = int(data["current"])
            try:
                await self._update_time_actions()
            except Exception as e:
                print(e,self.agent_type)
            update_status = {"Time":"Synced"}
        except KeyError as e:
            print(e)
            update_status = {"Time":"Asynced"}
        return update_status

    def get_html_status_data(self):
        pass

    def _update_time_actions(self):
        pass

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
    def __init__(self,agent_uuid, agent_type,config):
        super().__init__(agent_uuid=agent_uuid,agent_type=agent_type,config=config)
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
                time.sleep(random.randint(30,60))
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
                        time.sleep(random.randint(30, 60))
                        indicator=self._generate_indicator(url)
                        if indicator:
                            software_indicators.append(indicator)
            indicators[software_id]=software_indicators
        return indicators

    def _generate_indicator(self,url:str):
        generated_indicators=None
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            print(f"{response.status_code} - {url}")
            if url.endswith('pdf'):
                generated_indicators=self._query_ai_for_indicators(response.content,suffix=".pdf")
            else:
                try:
                    configwk = pdfkit.configuration(wkhtmltopdf=os.path.abspath(self.config['wkhtmltopdf_path']))
                    pdf_bytes = pdfkit.from_url(url, output_path=False, configuration=configwk)
                    pdf_buffer = BytesIO(pdf_bytes)
                    pdf_buffer.seek(0)
                    generated_indicators = self._query_ai_for_indicators(pdf_buffer.getvalue(), suffix=".pdf")
                except OSError as e:
                    print(e)
        except requests.exceptions.RequestException as e:
            print(e)
        return generated_indicators


    def _query_ai_for_indicators(self, content,suffix=".pdf"):
        with (tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp):
            try:
                tmp.write(content)
                tmp_path = tmp.name
                vector_store = self.openai.client.vector_stores.create(name="Report file")
                file_streams = [open(tmp_path, 'rb')]
                file_batch = self.openai.client.vector_stores.file_batches.upload_and_poll(
                    vector_store_id=vector_store.id,
                    files=file_streams)
                print(f"File upload {file_batch.status}")
                responseq = self.openai.client.responses.create(
                    model=self.config['openai_model'],
                    input="Generate the indicators of compromise of  the uploaded document following the stix v2 schema in json format",
                    tools=[{
                        "type": "file_search",
                        "vector_store_ids": [vector_store.id]
                        }])
                generated_indicators = self._extract_stix_indicators(responseq.output_text)
            except openai.RateLimitError as e:
                print(e)
                time.sleep(60)
                generated_indicators = None
            except openai.BadRequestError as a:
                print(a)
                generated_indicators = None
            return generated_indicators

    def _extract_stix_indicators(self,response):
        if self._extract_code_blocks(response):
            extracted_json_text= self._extract_code_blocks(response)[0]
            try:
                data = json.loads(extracted_json_text)
            except json.JSONDecodeError:
            #If the assistant wrapped the JSON in markdown fences, strip them:
                cleaned = response.strip("```json\n").rstrip("```").strip()
                try:
                    data = json.loads(cleaned)
                except json.JSONDecodeError as e:
                    print(e)
                    print(cleaned)
                    data = None
        else:
            data= None
        return data

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

    def __init__(self,agent_uuid,agent_type,config,custom=False):
        super().__init__(agent_uuid=agent_uuid,agent_type=agent_type,config=config)
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

    def __init__(self,config,agent_uuid="00000000",agent_type="MITREATTCK"):
        super().__init__(agent_uuid=agent_uuid,agent_type=agent_type,config=config)
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

class MITRED3FENDConfig:

    def __init__(self,config):
        self.config=config
        self.vulnerabilities=[]
        self.graph=Graph()
        self.graph.parse(source=f"file:///{self.config['d3fend_path']}",format='xml')
        self.skos=Namespace("http://www.w3.org/2004/02/skos/core#")
        self.d3fend=Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")
        self.dcterms=Namespace("http://purl.org/dc/terms/")
        self.initNS={"d3f":self.d3fend,"dcterms":self.dcterms}
        self.d3fend_kb=self.create_d3fend_knowledge_base()

    def get_vulnerabilities(self):
        high_severity_vulnerabilities=nvdlib.searchCVE(cvssV3Severity="HIGH",limit=5)
        print(high_severity_vulnerabilities)
        self.vulnerabilities=high_severity_vulnerabilities

    def create_d3fend_knowledge_base(self):
        tactics = self.get_d3fend_tactics()
        techniques_categories={}
        techniques={}
        for key, tactic in tactics.items():
            techniques_categories[key] = self.get_d3fend_techniques_categories(key)
            for key1, technique_cat in techniques_categories[key].items():
                techniques[key1]=self.get_d3fend_techniques(key1)
        d3fend_kb={"tactics":tactics,"techniques_categories":techniques_categories,"techniques":techniques}
        return d3fend_kb


    def get_d3fend_tactics(self):
        tactics={}
        sparql_query = prepareQuery(
            "SELECT ?name ?label ?definition ?ida WHERE { ?name a d3f:DefensiveTactic; rdfs:label ?label ;d3f:definition ?definition;.}",
            initNs=self.initNS)
        query_result = self.graph.query(sparql_query, )
        for row in query_result:
            tactics[row.name]=row.label
        return tactics

    def get_d3fend_techniques_categories(self,tactic):
        techniques_cat={}
        sparql_query = prepareQuery("SELECT ?name ?label ?definition ?ida WHERE { ?name a ?name ; rdfs:label ?label ;d3f:definition ?definition; d3f:d3fend-id ?ida ;d3f:enables ?tactic.}",initNs=self.initNS)
        query_result = self.graph.query(sparql_query,initBindings={"tactic":tactic} )
        for row in query_result:
            techniques_cat[row.name]=row.label
        return techniques_cat

    def get_d3fend_techniques(self,technique_cat):
        techniques_cat={}
        sparql_query = prepareQuery("SELECT ?name ?label ?definition ?ida WHERE { ?name a ?name ; rdfs:label ?label ;d3f:definition ?definition; d3f:d3fend-id ?ida ;rdfs:subClassOf ?technique_cat .}",initNs=self.initNS)
        query_result = self.graph.query(sparql_query,initBindings={"technique_cat":technique_cat} )
        for row in query_result:
            techniques_cat[row.name]=row.label
        return techniques_cat


class CTISourceConfig:

    def __init__(self,config):
        self.config=config

    def get_pulsedive_data(self):
        auth = HTTPBasicAuth("taxii2", self.config['pulsedive_key'])
        srv = Server(self.config['discovery_url'], user=auth.username, password=self.config['pulsedive_key'])
        root = srv.api_roots[0]
        for c in root.collections:
            print(c.id, c.title)
        cti_data={}
        dict_key=0
        restricted_use=[self.config['indicators_collection'],self.config['threat_collection']]
        for col in root.collections:
            if col.id not in restricted_use:
                for page in as_pages(col.get_objects, per_request=200):
                    for obj in page.get("objects", []):
                        cti_data[f"{dict_key}-{col.id}"]=obj
                        print(obj)
                        print("-----------------------------------------")

        write_to_json(self.config['pulse_cti_store_data'],cti_data)

    def get_otx_data(self):
        auth = HTTPBasicAuth(self.config['otx_key'],"")
        srv = Server(self.config['otx_discovery'], user=auth.username, password=auth.password)
        root = srv.api_roots[0]
        col = root.collections[0]
        cti_data={}
        dict_key=0
        count = 0
        try:
            for page in as_pages(col.get_objects, per_request=200):
                for obj in page.get("objects", []):
                    count += 1
                    if count % 1000 == 0:
                        print(obj)
                    if count <= 3:
                        try:
                            typed = parse(obj, allow_custom=True)
                            print("Parsed:", getattr(typed, "type", obj.get("type")), getattr(typed, "name", ""))
                        except Exception:
                            pass
                    else:
                        cti_data[dict_key]=obj
                        dict_key+=1
        except Exception:
            pass
        write_to_json(self.config['otx_cti_store_data'],cti_data)

    def get_electiciq_data(self):
        client = create_client(discovery_path=self.config['electiciq_discovery'], use_https=True)
        collections = client.get_collections()
        print("Available collections:")
        for c in collections:
            print(f" - {c.name} (available={c.available})")
        collection_name = collections[1].name
        blocks = client.poll(collection_name=collection_name)
        cti_data={}
        dict_key=0
        for i, block in enumerate(blocks, start=1):
            content = block.content
            if not content:
                continue
            else:
                cti_data[dict_key]=content.decode("utf-8",errors="ignore")
                dict_key+=1

        print(f"Number of bundles: {dict_key}")
        write_to_json(self.config['electiciq_cti_store_data'],cti_data)

    def create_cti_source_pool(self):
        pulsedive_data=read_from_json(self.config['pulse_cti_store_data'])
        otx_cti_data=read_from_json(self.config['otx_cti_store_data'])
        electiciq_data=read_from_json(self.config['electiciq_cti_store_data'])


        cti_data_pool={}
        dict_key=0
        for key,value in pulsedive_data.items():
            cti_data_pool[dict_key]=value
            dict_key+=1

        for key,value in otx_cti_data.items():
            cti_data_pool[dict_key]=value
            dict_key+=1

        for key,value in electiciq_data.items():
            value_dict = json.loads(value)
            if "objects" in value_dict.keys():
                objs = value_dict["objects"]
                for obj in objs:
                    if "indicator" in obj["type"]:
                        cti_data_pool[dict_key]=obj
                        dict_key+=1
        print(f"CTI data pool size without attacker's data: {len(cti_data_pool.keys())}")
        for filename in os.listdir(self.config['experiments_data_path']):
            file_path = os.path.join(self.config['experiments_data_path'], filename)
            data = read_from_json(file_path)
            for key, value in data['indicators'].items():
                for item in value:
                    if item is not None:
                        for obj in item['objects']:
                            if "indicator" in obj['type']:
                                cti_data_pool[dict_key]=obj
                                dict_key+=1

        print(f"CTI data pool size: {len(cti_data_pool.keys())}")
        write_to_json(self.config['cti_data_pool'],cti_data_pool)