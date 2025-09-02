import random

import numpy
import numpy as np
from s4config.libconstants import IMPACT_LEVELS,CLASSIFICATION_LABELS,TYPES_OF_DATA

from s4lib.libbase import print_security_characteristics


class IA:

    def __init__(self,config):
        self.config = config
        key, value =random.choice(list(TYPES_OF_DATA.items()))
        self.key = key
        self.data_type=value
        self.expired=False

        if key == 1:
            self.confidentiality_key=random.randint(1,2)
            self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            self.integrity_key=random.randint(2,3)
            self.integrity=IMPACT_LEVELS[self.integrity_key]
            self.availability_key=random.choice([1,3])
            self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability_key))
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
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability_key))
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
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability_key))
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
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability_key))
            self.classification_key=random.randint(1,5)
            self.classification=CLASSIFICATION_LABELS[self.classification_key]
            self.lifespan = int(self.config["time_steps"]/8)
        else:
            print("Data type is not correct")


    def send_characteristics(self):
        return self.security_category,self.classification_key,self.lifespan

    def receive_compromised_status(self,status):
        if status == "compromised":
            self.lifespan=0

    def update_lifespan(self,time_step=1):
        if self.lifespan>0:
            self.lifespan-=time_step
            self.recalculate_characteristics()
        else:
            #self.__dict__.clear()
            self.expired = True

    def get_html_status_data(self):
        html_status_data = {'data_type': self.data_type, 'expired': self.expired,
                            'confidentiality': self.confidentiality, 'integrity': self.integrity,
                            'availability': self.availability, 'security_category': self.security_category,'classification': self.classification,
                            'lifespan': self.lifespan}
        return html_status_data

    def recalculate_characteristics(self):
        if self.key == 1:
            if self.confidentiality_key>1:
                self.confidentiality_key= self.sigmoid_integer(max_value=2,midpoint=int(self.config["time_steps"]/4))
                self.confidentiality=IMPACT_LEVELS[self.confidentiality_key]
            if self.integrity_key>2:
                self.integrity_key= self.sigmoid_integer(max_value=3,midpoint=int(self.config["time_steps"]/4))
                self.integrity=IMPACT_LEVELS[self.integrity_key]
            if self.availability_key>1:
                self.availability_key=self.sigmoid_integer(max_value=3,midpoint=int(self.config["time_steps"]/4))
                if self.availability_key==2:
                    self.availability_key = random.choice([1, 3])
                self.availability=IMPACT_LEVELS[self.availability_key]
            self.security_category=(("C",self.confidentiality_key),("I",self.integrity_key),("A",self.availability_key))
            if self.classification_key>2:
                self.classification_key=self.sigmoid_integer(max_value=4,midpoint=int(self.config["time_steps"]/4))
                self.classification=CLASSIFICATION_LABELS[self.classification_key]
        elif self.key == 2:
            if self.confidentiality_key > 2:
                self.confidentiality_key = self.sigmoid_integer(max_value=3,
                                                                midpoint=int(self.config["time_steps"] / 8))
                self.confidentiality = IMPACT_LEVELS[self.confidentiality_key]
            if self.integrity_key > 2:
                self.integrity_key = self.sigmoid_integer(max_value=3, midpoint=int(self.config["time_steps"] / 8))
                self.integrity = IMPACT_LEVELS[self.integrity_key]
            if self.availability_key > 2:
                self.availability_key = self.sigmoid_integer(max_value=3, midpoint=int(self.config["time_steps"] / 8))
                self.availability = IMPACT_LEVELS[self.availability_key]
            self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                      ("A", self.availability_key))
            if self.classification_key > 3:
                self.classification_key = self.sigmoid_integer(max_value=5, midpoint=int(self.config["time_steps"] / 8))
                self.classification = CLASSIFICATION_LABELS[self.classification_key]
        elif self.key == 3:
            if self.confidentiality_key > 1:
                self.confidentiality_key = self.sigmoid_integer(max_value=3,
                                                                midpoint=int(self.config["time_steps"] / 12))
                self.confidentiality = IMPACT_LEVELS[self.confidentiality_key]
            if self.availability_key > 1:
                self.availability_key = self.sigmoid_integer(max_value=2, midpoint=int(self.config["time_steps"] / 12))
                self.availability = IMPACT_LEVELS[self.availability_key]
            self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                      ("A", self.availability_key))
            if self.classification_key > 2:
                self.classification_key = self.sigmoid_integer(max_value=4, midpoint=int(self.config["time_steps"] / 12))
                self.classification = CLASSIFICATION_LABELS[self.classification_key]
        elif self.key == 4:
            if self.confidentiality_key > 1:
                self.confidentiality_key = self.sigmoid_integer(max_value=3,
                                                                midpoint=int(self.config["time_steps"] / 16))
                self.confidentiality = IMPACT_LEVELS[self.confidentiality_key]
            if self.integrity_key > 2:
                self.integrity_key = self.sigmoid_integer(max_value=3, midpoint=int(self.config["time_steps"] / 16))
                self.integrity = IMPACT_LEVELS[self.integrity_key]
            if self.availability_key > 1:
                self.availability_key = self.sigmoid_integer(max_value=2, midpoint=int(self.config["time_steps"] / 16))
                self.availability = IMPACT_LEVELS[self.availability_key]
            self.security_category = (("C", self.confidentiality_key), ("I", self.integrity_key),
                                      ("A", self.availability_key))
            if self.classification_key > 1:
                self.classification_key = self.sigmoid_integer(max_value=5, midpoint=int(self.config["time_steps"] / 16))
                self.classification = CLASSIFICATION_LABELS[self.classification_key]
        else:
            print("Data type is not correct")

    def sigmoid_integer(self,max_value,midpoint,k=0.5):
        return int(np.round(max_value / (1 + np.exp(-k * (self.lifespan - midpoint)))))


    def print_ia_security_characteristics(self):
        print_security_characteristics(self.security_category,self.confidentiality,self.integrity,self.availability,self.classification,self.classification_key)

