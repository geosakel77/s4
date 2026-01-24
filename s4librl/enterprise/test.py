from s4librl.enterprise.librlcti import AgCTIAlgRunner
from s4librl.enterprise.librlcticli import CTIRLClient
import threading
from s4config.libconstants import CONFIG_PATH
from s4config.libconfig import read_config

if __name__ == "__main__":
    config = read_config(CONFIG_PATH)
    agctialgrunner=AgCTIAlgRunner(CONFIG_PATH)



    cti_rl_client = CTIRLClient(config)
    threading.Thread(target=cti_rl_client.run).start()
    agctialgrunner.run_on_tune(tune_callbacks=[])


