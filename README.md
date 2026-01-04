# 📘 **Qualitative Assessment and Application of CTI based on Reinforcement Learning**

*This project is the implementation and experimental testing of the qualitative assessment and application of CTI based on the utilization of reinforcement learning in simulated enterprise environments publication.*

---

## **Table of Contents**

1. [Introduction](#introduction)  
2. [Objectives](#objectives)  
3. [Background and Theory](#background-and-theory)  
4. [Infrastructure](#infrastructure)
5. [Dataset](#dataset)
6. [Dependencies](#dependencies)  
7. [Usage](#usage)
8. [License](#license)  

---

## **Introduction**

S4 is the technical implementation of an infrastructure which experimentally integrates reinforcement learning in the qualitative assessment 
and application of CTI in enterprise environments, and it is based on the proposed solution in a paper under development. 
The goal of S4 is to implement the experimental infrastructure and to provide the means of reproducing the experimental results of the paper. 

---
## **Objectives**

- To develop the proposed architecture for the metric measurement.  
- To implement the mechanisms that measures the metrics. 
- To execute a number of experiments in hypothetical organizations.

---

## **Background and Theory**

### Relevant Theory
The relevant theory involved in the implementation of this project are related to:
- CTI.   
- Reinforcement Learning, and  
- CTI quality metrics

### Literature Review
This project leverages previous work on CTI systems modeling and CTI quality metrics development.

---

## **Infrastructure**
This project implements the infrastructure described in the following image:
![Experimental Infrastructure](https://github.com/geosakel77/s4/blob/master/images/exp_env_diagram.png)

There are six types of agents interacting within the environment: 

- Threat Actor Agents (TA)
- Cyber Threat Intelligence Agent (AgCTI)
- Defence Mechanisms Agents (DM)
- Cyber Threat Intelligence Sources Agents (SRC)
- Information Systems Agents (IS)
- Information Assets Agents (IA)

The interactions between the agents within the experimental infrastructure are illustrated in the following image:
![Agents Interactions](https://github.com/geosakel77/s4/blob/master/images/all_intercations_diagram.png)

### Utilization of MITRE D3FEND for DM agents Construction
The project utilize the MITRE D3FEND knowledge base to contract the three types of DM agents, namely:

- Preventive
- Detective
- Responsive

The following image illustrates the utilization of MITRE D3FEND by the S4: 
![Utilization of MITRE D3FEND](https://github.com/geosakel77/s4/blob/master/images/dm_d3fend_util.png)


### Generic Infrastructure Testing

[![Demo Video](https://youtu.be/T92mEr7962k)]

---

## **Dataset**

### Experimental Dataset Description – TA Dataset & CTI Pool

This repository documents the datasets and statistics used in the experimental evaluation.
The primary sources of data for the development of the datasets are the following: 
- **MITRE ATT&CK** knowledge base.
- **Pulsedive** Community
- **AlienVault OTX**
- **EclecticIQ**

In general, the project uses two dataset of indicators; the one used by the threat actor agents (TA Dataset) and the other used by the CTI source agents (CTI Pool). 
The first one is 90% subset of the second. 

### TA Dataset Overview

- **Total number of Threat Actors in MITRE ATT&CK:** 150
- **Threat Actors used in experiments:** 33

The selected threat actors were chosen to ensure diversity in:
- number of indicators
- number of techniques
- observable pattern coverage
- supported platforms

This enables analysis of observable skew, actor representativeness, and CTI coverage limitations.

#### Threat Actors and Characteristics

Each threat actor is characterized using four dimensions:

- **Indicators**: Total number of indicators attributed to the actor  
- **Techniques**: Associated ATT&CK techniques  
- **Patterns**: Distinct observable patterns  
- **Platforms**: Applicable platforms  

| Threat Actor | Indicators | Techniques | Patterns | Platforms |
|--------------|------------|------------|----------|-----------|
| GALLIUM | 154 | 31 | 6 | 11 |
| APT17 | 8 | 2 | 1 | 1 |
| APT41 | 409 | 134 | 14 | 11 |
| menuPass | 276 | 46 | 10 | 11 |
| MuddyWater | 230 | 58 | 7 | 11 |
| Gamaredon Group | 54 | 55 | 5 | 10 |
| Leafminer | 23 | 17 | 7 | 11 |
| FIN7 | 161 | 53 | 13 | 11 |
| Machete | 75 | 11 | 6 | 8 |
| ZIRCONIUM | 0 | 29 | 0 | 11 |
| Rocke | 4 | 36 | 4 | 7 |
| Orangeworm | 0 | 2 | 0 | 5 |
| Taidoor | 0 | 0 | 0 | 0 |
| APT34 | 0 | 0 | 0 | 0 |
| APT1 | 28 | 23 | 6 | 11 |
| Blue Mockingbird | 15 | 22 | 2 | 8 |
| SilverTerrier | 67 | 4 | 6 | 7 |
| Dragonfly 2.0 | 41 | 0 | 6 | 0 |
| FIN5 | 21 | 11 | 10 | 11 |
| Mofang | 10 | 6 | 4 | 6 |
| Lotus Blossom | 30 | 21 | 7 | 10 |
| BRONZE BUTLER | 721 | 40 | 8 | 11 |
| MONSOON | 0 | 0 | 0 | 0 |
| Whitefly | 22 | 9 | 3 | 10 |
| Metador | 1 | 9 | 0 | 6 |
| APT-C-36 | 5 | 9 | 4 | 6 |
| FIN4 | 0 | 12 | 0 | 10 |
| Thrip | 0 | 4 | 0 | 6 |
| Wizard Spider | 172 | 64 | 12 | 11 |
| Molerats | 391 | 16 | 8 | 8 |
| PROMETHIUM | 68 | 11 | 10 | 8 |
| DragonOK | 120 | 0 | 6 | 0 |
| Rancor | 0 | 9 | 0 | 5 |

#### Repository-Level Statistics
- **Total indicators:** 3,106  
- **Total techniques:** 239  
- **Total observable patterns:** 24  
- **Total platforms:** 11  

The distribution of the observable patterns within TA Dataset is illustrated the following pie chart: 

![Observable Patterns within TA Dataset](https://github.com/geosakel77/s4/blob/master/images/pie_ta_patterns_data.png)

### CTI Pool Overview
The CTI Pool dataset is constructed by data collected form all four sources and provides a pool of indicators to the CTI sources agents. 


#### Repository-Level Statistics

- **Total indicators:** 10,227  
- **Total observable patterns:** 26  

- The distribution of the observable patterns within TA Dataset is illustrated the following pie chart: 

![Observable Patterns within CTI Pool Dataset](https://github.com/geosakel77/s4/blob/master/images/pie_src_patterns_data.png)


### Experimental Relevance

These datasets enable:
- analysis of **observable dominance and bias**
- evaluation of the **experimental CTI sources**
- comparison between **actor-specific intelligence** and **generic CTI pools**

### Notes

- Threat actors with zero indicators or patterns are intentionally preserved to reflect **real-world data sparsity**
- Platform diversity is capped at 11 by the ATT&CK knowledge base
- All statistics were extracted programmatically to ensure reproducibility

---

## **Dependencies**

- Language: Python (>= 3.11)  
- Libraries: antlr4-python3-runtime (4.9.3), anyio (4.9.0), arrow (1.4.0), attrs (25.4.0), Brotli (1.1.0), cabby (0.1.23), certifi (2025.7.14), cffi (1.17.1), charset-normalizer (3.4.2), click (8.2.1), colorama (0.4.6), colorlog (6.10.1), colour (0.1.5), commonmark (0.9.1), contourpy (1.3.3), cpe (1.3.1), cssselect2 (0.8.0), cybox (2.1.0.21), cycler (0.12.1), deepdiff (8.5.0), distro (1.9.0), drawsvg (2.4.0), et_xmlfile (2.0.0), fastapi (0.116.1), fire (0.4.0), fonttools (4.59.0), fqdn (1.5.1), furl (2.1.4), h11 (0.16.0), httpcore (1.0.9), httpx (0.28.1), idna (3.1), importlib-metadata (3.3.0), isoduration (20.11.0), Jinja2 (3.1.6), jiter (0.10.0), jsonpointer (3.0.0), jsonschema (4.25.1), jsonschema-specifications (2025.9.1), kiwisolver (1.4.9), lark (1.3.0), libtaxii (1.1.119), loguru (0.7.3), lxml (6.0.2), maec (4.1.0.17), Markdown (3.8.2), markdown-it-py (3.0.0), MarkupSafe (3.0.2), matplotlib (3.10.8), mdurl (0.1.2), mitreattack-python (4.0.2), mixbox (1.0.5), netaddr (1.3.0), numpy (2.2.3), nvdlib (0.8.2), openai (1.97.0), openpyxl (3.1.5), ordered-set (4.1.0), orderedmultidict (1.0.1), orderly-set (5.5.0), packaging (25), pandas (2.2.3), pandas-stubs (2.3.2.250926), pdfkit (1.0.0), pillow (11.3.0), platformdirs (4.3.8), pluralizer (2.0.0), pooch (1.8.2), pyattck (7.1.2), pyattck-data (2.6.3), pycountry (24.6.1), pycparser (2.22), pydantic (1.10.22), pydyf (0.11.0), Pygments (2.19.2), pyparsing (3.2.3), pyphen (0.17.2), python-dateutil (2.9.0.post0), pytz (2025.1), PyYAML (6.0.2), rdflib (7.1.4), referencing (0.37.0), requests (2.30.0), rfc3339-validator (0.1.4), rfc3986-validator (0.1.1), rfc3987-syntax (1.1.0), rich (12.6.0), rpds-py (0.28.0), shellingham (1.5.4), simplejson (3.20.1), six (1.17.0), sniffio (1.3.1), starlette (0.47.2), stix (1.2.0.11), stix-edh (1.0.3), stix2 (3.0.1), stix2-elevator (4.1.7), stix2-patterns (2.0.0), stix2-validator (3.2.0), stixmarx (1.0.8), tabulate (0.9.0), taxii2-client (2.3.0), termcolor (3.1.0), tinycss2 (1.4.0), tinyhtml5 (2.0.0), tqdm (4.67.1), typer (0.16.0), typing_extensions (4.14.1), tzdata (2025.1), uri-template (1.3.0), urllib3 (2.5.0), uvicorn (0.35.0), weakrefmethod (1.0.3), weasyprint (66), webcolors (24.11.1), webencodings (0.5.1), win32_setctime (1.2.0), xlsxwriter (3.2.5), zipp (3.23.0), zopfli (0.2.3.post1)
- OS: Ubuntu 24.04, Windows 11  

---

## **Usage**

### Installation
1. Clone the repository:  
   ```bash
   git clone https://github.com/geosakel77/s4.git
   cd s4
2. Rename and edit the configuration file. Complete the missing values in brackets.
   ```bash
   mv ./s4config/config_example.ini ./s4config/config.ini
   vi config.ini
   
3. Run the following scripts
   - Run setup.py 
   - Run coordiantor.py
   - Run main.py

## **License**
    
```markdown
    
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
    