import json
from config.libconfig import read_config
from config.libconstants import MAP_TECHNIQUES_TO_TACTICS
from pyattck import Attck
from typing import  Any
from openai import OpenAI
from stix2 import FileSystemStore,Filter
from pprint import pprint

def write_to_json(json_file,json_data):
    with open(json_file,'w') as outfile:
        json.dump(json_data,outfile)

def read_from_json(json_file):
    with open(json_file,'r') as infile:
        json_data = json.load(infile)
        return json_data

class Agent:
    def __init__(self,agent_type,config_file='C:\\Users\\geosa\\PycharmProjects\\s4\\config\\config.ini'):
        self.agent_type=agent_type
        self.config=read_config(config_file)


class OpenAIClient:
    def __init__(self, config):
        self.config=config
        self.client = OpenAI(api_key=self.config['openai_api_key'], organization=self.config['openai_organization_id'],
                             project=self.config['openai_project_id'])

    def call_openai(self, message):
        messages_list: list[dict[str, str | Any]] = [{
            "role": "user",
            "content": message
        }]
        response = self._call_run(messages_list)
        return response

    def _call_run(self, messages_list):
        return self.client.chat.completions.create(messages=messages_list, model=self.config['openai_model'],
                                                   temperature=0).choices[
            0].message.content


class AttackerAgent(Agent):
    def __init__(self, agent_type,use_local=False):
        super().__init__(agent_type=agent_type)
        self.use_local=use_local
        if self.use_local:
            self.mitre_attack=FileSystemStore(self.config['mitre_enterprise_path'])
        else:
            self.mitre_attack = Attck(nested_techniques=True, use_config=True,
                                  config_file_path=self.config['pyattck_path'],
                                  data_path=self.config['pyattck_data'],
                                  enterprise_attck_json=self.config['enterprise_attck_path'],
                                  generated_nist_json=self.config['generated_nist_path'],
                                  ics_attck_json=self.config['ics_attck_path'],
                                  mobile_attck_json=self.config['mobile_attck_path'],
                                  nist_controls_json=self.config['nist_controls_path'],
                                  pre_attck_json=self.config['pre_attck_path'])

    def remove_revoked_deprecated(self,stix_objects):
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
        if self.use_local:
            thesrc = self.mitre_attack
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
    def software_used_by_groups(self,thesrc):
        """returns group_id => {software, relationship} for each software used by the group and each software used by campaigns attributed to the group."""
        # get all software used by groups
        if self.use_local:
            thesrc=self.mitre_attack
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

    def groups_using_software(self,thesrc):
        """returns software_id => {group, relationship} for each group using the software and each software used by attributed campaigns."""
        # get all groups using software
        if self.use_local:
            thesrc=self.mitre_attack
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
    def techniques_used_by_groups(self,thesrc):
        """returns group_id => {technique, relationship} for each technique used by the group and each
           technique used by campaigns attributed to the group."""
        # get all techniques used by groups
        if self.use_local:
            thesrc= self.mitre_attack
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

    def groups_using_technique(self,thesrc):
        """returns technique_id => {group, relationship} for each group using the technique and each campaign attributed to groups using the technique."""
        # get all groups using techniques
        if self.use_local:
            thesrc = self.mitre_attack
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
    def techniques_used_by_software(self,thesrc):
        """return software_id => {technique, relationship} for each technique used by the software."""
        if self.use_local:
            thesrc = self.mitre_attack
        techniques_by_tool = self.get_related(thesrc, "tool", "uses", "attack-pattern")
        techniques_by_malware = self.get_related(thesrc, "malware", "uses", "attack-pattern")
        return {**techniques_by_tool, **techniques_by_malware}

    def software_using_technique(self,thesrc):
        """return technique_id  => {software, relationship} for each software using the technique."""
        if self.use_local:
            thesrc = self.mitre_attack
        tools_by_technique_id = self.get_related(thesrc, "tool", "uses", "attack-pattern", reverse=True)
        malware_by_technique_id = self.get_related(thesrc, "malware", "uses", "attack-pattern", reverse=True)
        return {**tools_by_technique_id, **malware_by_technique_id}

    # technique:mitigation
    def mitigation_mitigates_techniques(self,thesrc):
        """return mitigation_id => {technique, relationship} for each technique mitigated by the mitigation."""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "course-of-action", "mitigates", "attack-pattern", reverse=False)

    def technique_mitigated_by_mitigations(self,thesrc):
        """return technique_id => {mitigation, relationship} for each mitigation of the technique."""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "course-of-action", "mitigates", "attack-pattern", reverse=True)

    # technique:sub-technique
    def subtechniques_of(self,thesrc):
        """return technique_id => {subtechnique, relationship} for each subtechnique of the technique."""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "attack-pattern", "subtechnique-of", "attack-pattern", reverse=True)

    def parent_technique_of(self,thesrc):
        """return subtechnique_id => {technique, relationship} describing the parent technique of the subtechnique"""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "attack-pattern", "subtechnique-of", "attack-pattern")[0]

    # technique:data-component
    def datacomponent_detects_techniques(self,thesrc):
        """return datacomponent_id => {technique, relationship} describing the detections of each data component"""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "x-mitre-data-component", "detects", "attack-pattern")

    def technique_detected_by_datacomponents(self,thesrc):
        """return technique_id => {datacomponent, relationship} describing the data components that can detect the technique"""
        if self.use_local:
            thesrc = self.mitre_attack
        return self.get_related(thesrc, "x-mitre-data-component", "detects", "attack-pattern", reverse=True)

class MITREATTCKConfig(AttackerAgent):

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
            actors[actor.id]=actor.name
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


    def _create_actors_indicators(self):
        for actor in self.mitre_attack.enterprise.actors:
            #TODO
            pass



