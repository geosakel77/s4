
from mitreattack.stix20 import MitreAttackData
from stix2 import FileSystemStore


if __name__=="__main__":

    src = FileSystemStore('C:\\Users\\geosa\\PycharmProjects\\s4\\config\\mitreattckdata\\enterprise-attack')
    data=src.get('intrusion-set--3ea7add5-5b8f-45d8-b1f1-905d2729d62a')
    print(data)