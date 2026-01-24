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
MAP_TECHNIQUES_TO_TACTICS = {
"TA0043":["T1595","T1596","T1597","T1598","T1599","T1600","T1601","T1602","T1603","T1604"],
"TA0042":["T1650","T1583","T1586","T1584","T1587","T1585","T1588","T1608"],
"TA0001":["T1659","T1189","T1190","T1133","T1200","T1566","T1091","T1195","T1199","T1078","T1669"],
"TA0002":["T1651","T1059","T1609","T1610","T1675","T1203","T1674","T1559","T1106","T1053","T1648","T1129","T1072","T1569","T1204","T1047"],
"TA0003":["T1098","T1197","T1547","T1037","T1671","T1554","T1136","T1543","T1546","T1668","T1133","T1574","T1525","T1556","T1112","T1137","T1653","T1542","T1053","T1505","T1176","T1205","T1078"],
"TA0004":["T1548","T1134","T1098","T1547","T1037","T1543","T1484","T1611","T1546","T1068","T1574","T1055","T1053","T1078"],
"TA0005":["T1548","T1134","T1197","T1612","T1622","T1140","T1610","T1006","T1484","T1672","T1480","T1211","T1222","T1564","T1574","T1562","T1656","T1070","T1202","T1036","T1556","T1578","T1666","T1112","T1601","T1599","T1027","T1647","T1542","T1055","T1620","T1207","T1014","T1553","T1218","T1216","T1221","T1205","T1127","T1535","T1550","T1078","T1497","T1600","T1220"],
"TA0006":["T1557","T1110","T1555","T1212","T1187","T1606","T1056","T1556","T1111","T1621","T1040","T1003","T1528","T1649","T1558","T1539","T1552"],
"TA0007":["T1087","T1010","T1217","T1580","T1538","T1526","T1619","T1613","T1622","T1652","T1482","T1083","T1615","T1654","T1046","T1135","T1040","T1201","T1120","T1069","T1057","T1012","T1018","T1518","T1082","T1614","T1016","T1049","T1033","T1007","T1124","T1673","T1497"],
"TA0008":["T1210","T1534","T1570","T1563","T1021","T1091","T1072","T1080","T1550"],
"TA0009":["T1557","T1560","T1123","T1119","T1185","T1115","T1530","T1602","T1213","T1005","T1039","T1025","T1074","T1114","T1056","T1113","T1125"],
"TA0010":["T1020","T1030","T1048","T1041","T1011","T1052","T1567","T1029","T1537"],
"TA0011":["T1071","T1092","T1659","T1132","T1001","T1568","T1573","T1008","T1665","T1105","T1104","T1095","T1571","T1572","T1090","T1219","T1205","T1102"],
"TA0040":["T1531","T1485","T1486","T1565","T1491","T1561","T1667","T1499","T1657","T1495","T1490","T1498","T1496","T1489","T1529"],
}
MAP_TACTICS_TO_NAMES={"TA0043":"reconnaissance","TA0042":"resource-development","TA0001":"initial-access","TA0002":"execution","TA0003":"persistence","TA0004":"privilege-escalation","TA0005":"defense-evasion","TA0006":"credential-access","TA0007":"discovery","TA0008":"lateral-movement","TA0009":"collection","TA0011":"command-and-control","TA0010":"exfiltration","TA0040":"impact"}
CONFIG_PATH='C:\\Users\\geosa\\PycharmProjects\\s4\\s4config\\config.ini'
AGENT_TYPES={1:"TA",2:"DM",3:"CTI",4:"IS",5:"SRC"}
DM_TYPES={1:"Preventive",2:"Detective",3:"Responsive"}
IMPACT_LEVELS={1:"L",2:"M",3:"H"}
TYPES_OF_DATA={1:"Reference Data",2:"Master Data",3:"Metadata",4:"Transactional Data"}
CLASSIFICATION_LABELS={5:"S",4:"C",3:"Pri",2:"Pro",1:"Pu"}
IND_TYPES={"Preventive":['vulnerability','vulnerability:name','x509-certificate:serial_number','windows-registry-key:key'],
           "Detective":['rule','file:name','malware:name','email-addr:value','url:value','file:hashes.SHA256','artifact:payload_bin','x-crypto-address:value','process:name','process:mutexes[*]', 'process:command_line', 'process:mutexes*.name','rule', 'mutex:value', 'domain-name:value','mutex:name','network-traffic:extensions','x509-certificate:serial_number','network-traffic:user_agent',  'directory:path','file:hashes.imphash','network-traffic:dst_port', 'file:hashes.SHA1','file:parent_directory_ref.path','file:hashes', 'file:hashes.SHA-256', 'ipv4-addr:value','email-message:from_ref.value','network-traffic:extensions.http-request-ext.request_header.User-Agent','file:parent_directory_ref','file:path','file:hashes.MD5','network-traffic:extensions.http-request-ext.request_uri','network-traffic:extensions.http-request-ext.request_header.X-Not-Malware',],
           "Responsive":['file:name','malware:name','file:hashes.SHA256','artifact:payload_bin', 'mutex:value','mutex:name','process:name','process:mutexes[*]','process:command_line', 'process:mutexes*.name', 'domain-name:value', 'directory:path','file:hashes.imphash', 'file:parent_directory_ref.path','file:hashes', 'file:hashes.SHA-256', 'file:parent_directory_ref','file:hashes.SHA-1','file:path','file:hashes.MD5','windows-registry-key:key']}
PLATFORM_TYPES=['SaaS', 'Containers', 'Linux', 'Identity Provider', 'Windows', 'Network Devices', 'Office Suite', 'IaaS', 'macOS', 'ESXi', 'PRE']
EXPERIMENTS_ACTORS=['GALLIUM', 'APT17', 'APT41', 'menuPass', 'MuddyWater', 'Gamaredon Group', 'Leafminer', 'FIN7', 'Machete', 'ZIRCONIUM', 'Rocke', 'Orangeworm', 'Taidoor', 'APT34', 'APT1', 'Blue Mockingbird', 'SilverTerrier', 'Dragonfly 2.0', 'FIN5', 'Mofang', 'Lotus Blossom', 'BRONZE BUTLER', 'MONSOON', 'Whitefly', 'Metador', 'APT-C-36', 'FIN4', 'Thrip', 'Wizard Spider', 'Molerats', 'PROMETHIUM', 'DragonOK', 'Rancor']
RL_FEATURES_DICT_1={'network-traffic:user_agent': 0, 'domain-name:value': 1, 'rule': 2, 'vulnerability:name': 3, 'mutex:name': 4, 'directory:path': 5, 'file:parent_directory_ref': 6, 'file:path': 7, 'ipv4-addr:value': 8, 'file:hashes': 9, 'process:command_line': 10, 'malware:name': 11, 'network-traffic:dst_port': 12, 'mutex:value': 13, 'process:name': 14, 'artifact:payload_bin': 15, 'url:value': 16, 'x-crypto-address:value': 17, 'process:mutexes[*]': 18, 'file:name': 19, 'email-message:from_ref': 20, 'email-addr:value': 21, 'windows-registry-key:key': 22, 'x509-certificate:serial_number': 23, 'network-traffic:extensions': 24}
RL_FEATURES_DICT_2={'malicious-code': 0, 'file-hash-watchlist': 1, 'command-and-control': 2, 'malware-artifact': 3, 'anomoly': 4, 'malware-distribution': 5, 'vulnerability': 6, 'host-characteristics': 7, 'infrastructure': 8, 'malicious-activity': 9, 'download-url': 10, 'anomalous-activity': 11, 'benign': 12, 'anomalous-traffic': 13, 'malware': 14, 'compromised': 15, 'ip-watchlist': 16, 'host-behavior': 17}
RL_FEATURES_DICT_TO_TYPES={'network-traffic:user_agent': ['command-and-control','malicious-activity','anomalous-activity','anomalous-traffic'],'domain-name:value': ['command-and-control','anomalous-activity','anomalous-traffic','malware-distribution'],'rule': ['malicious-activity','download-url','malware'],'vulnerability:name': ['vulnerability'],'mutex:name': ['malicious-code','host-behavior'],'directory:path': ['malware-artifact'],'file:parent_directory_ref': ['file-hash-watchlist'],'file:path': ['file-hash-watchlist','malware-artifact','malicious-code'],'ipv4-addr:value': ['command-and-control','ip-watchlist'],'file:hashes': ['malicious-activity','file-hash-watchlist','malware-artifact'],'process:command_line': ['malicious-activity','malicious-code'],'malware:name': ['malicious-activity','malware','malware-artifact'],'network-traffic:dst_port': ['command-and-control','malware-distribution'],'mutex:value': ['malicious-activity','malware','host-behavior'],'process:name': ['malicious-activity','malware','host-behavior'],'artifact:payload_bin': ['malicious-activity','malware'],'url:value': ['command-and-control','download-url'],'x-crypto-address:value': ['command-and-control','malicious-activity'],'process:mutexes[*]': ['malware','malware-artifact'], 'file:name': ['file-hash-watchlist','malware-artifact'],'email-message:from_ref': ['download-url','anomalous-activity','anomalous-traffic','malware-distribution'],'email-addr:value': ['anomalous-activity','anomalous-traffic'],'windows-registry-key:key': ['malware', 'infrastructure'],'x509-certificate:serial_number': ['host-characteristics', 'infrastructure'],'network-traffic:extensions': ['command-and-control','anomalous-activity','anomalous-traffic']}