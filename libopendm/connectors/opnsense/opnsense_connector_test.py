from libopendm.connectors.opnsense.opnsense_connector import OPNSenseConnector


if __name__ == "__main__":
    connector = OPNSenseConnector()
    connector.get_fw_ids_status()
    #connector.get_fw_ids_settings()
    #connector.get_fw_ids_rulesets()
    #connector.get_fw_ids_user_rules()
    connector.get_fw_ids_policy()
    connector.search_fw_ids_policy()
    connector.add_fw_ids_policy()
    #connector.get_fw_ids_policy_rules()
