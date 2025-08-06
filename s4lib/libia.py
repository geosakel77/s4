import random
from config.libconstants import IMPACT_LEVELS,CLASSIFICATION_LABELS,TYPES_OF_DATA


class TA:

    def __init__(self,config):
        self.config = config
        key, value =random.choice(list(TYPES_OF_DATA.items()))
        self.data_type=value

        if key == 1:
            self.confidentiality_key=random.randint(1,2)
            self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            self.integrity_key=random.randint(2,3)
            self.integrity=IMPACT_LEVELS[self.integrity_key]
            self.availability_key=random.choice([1,3])
            self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability))
            self.classification_key=random.randint(2,4)
            self.classification=CLASSIFICATION_LABELS[self.classification_key]
            self.lifespan = int(self.config["time_steps"]/2)
        elif key == 2:
            self.confidentiality_key=random.randint(2,3)
            self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            self.integrity_key=random.randint(2,3)
            self.integrity=IMPACT_LEVELS[self.integrity_key]
            self.availability_key=random.randint(2,3)
            self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability))
            self.classification_key=random.randint(3,5)
            self.classification=CLASSIFICATION_LABELS[self.classification_key]
            self.lifespan = int(self.config["time_steps"]/4)
        elif key == 3:
            self.confidentiality_key=random.randint(1,3)
            self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            self.integrity_key=2
            self.integrity=IMPACT_LEVELS[self.integrity_key]
            self.availability_key=random.randint(1,2)
            self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability))
            self.classification_key=random.randint(2,4)
            self.classification=CLASSIFICATION_LABELS[self.classification_key]
            self.lifespan = int(self.config["time_steps"]/6)
        elif key == 4:
            self.confidentiality_key=random.randint(1,3)
            self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            self.integrity_key=random.randint(2,3)
            self.integrity=IMPACT_LEVELS[self.integrity_key]
            self.availability_key=random.randint(1,2)
            self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability))
            self.classification_key=random.randint(1,5)
            self.classification=CLASSIFICATION_LABELS[self.classification_key]
            self.lifespan = int(self.config["time_steps"]/8)
        else:
            print("Data type is not correct")


    def send_characteristics(self):
        return self.security_category,self.classification,self.lifespan


    def receive_compromised_status(self,status):
        if status == "compromised":
            self.lifespan=0

    def update_lifespan(self,time_step=1):
        if self.lifespan>0:
            self.lifespan-=time_step
        else:
            self.__dict__.clear()

    def recalculate_characteristics(self):
        #TODO
        pass