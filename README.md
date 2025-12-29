# Experimental Dataset Description – MITRE ATT&CK Threat Actors & CTI Pool

This repository documents the datasets and statistics used in the experimental evaluation of Cyber Threat Intelligence (CTI) quality metrics and system modeling, grounded on threat actors from the **MITRE ATT&CK** knowledge base and an external CTI pool.

---

## 1. Threat Actors Overview

- **Total number of Threat Actors in MITRE ATT&CK:** 150
- **Threat Actors used in experiments:** 33

The selected threat actors were chosen to ensure diversity in:
- number of indicators
- number of techniques
- observable pattern coverage
- supported platforms

This enables analysis of observable skew, actor representativeness, and CTI coverage limitations.

---

## 2. Threat Actors and Characteristics

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

---

## 3. Repository-Level Statistics

### Threat Actor Repository
- **Total indicators:** 3,106  
- **Total techniques:** 239  
- **Total observable patterns:** 24  
- **Total platforms:** 11  

### CTI Pool Repository
- **Total indicators:** 10,227  
- **Total observable patterns:** 26  

---

## 4. Observable Pattern Distribution

The distribution of observable patterns is highly skewed, with a small number of patterns dominating the dataset.

### Top-5 Patterns
1. `file:hashes`
2. `domain-name:value`
3. `url:value`
4. `ipv4-addr:value`
5. `file:name`

---

## 5. Visualizations

### 5.1 Top-5 vs Others (Pie Chart)

This pie chart highlights the dominance of the five most frequent observable patterns, while aggregating the remaining patterns as **Others**.

![Top-5 Patterns vs Others – Pie Chart](images/top5_vs_others_pie.png)

---

### 5.2 Top-5 Patterns (Bar Chart)

The bar chart emphasizes the steep frequency drop between dominant and secondary observable types.

![Top-5 Patterns – Bar Chart](images/top5_patterns_bar.png)

---

## 6. Experimental Relevance

These datasets enable:
- analysis of **observable dominance and bias**
- evaluation of **CTI relevance and actionability**
- comparison between **actor-specific intelligence** and **generic CTI pools**
- stress-testing of CTI quality metrics under skewed distributions

---

## 7. Notes

- Threat actors with zero indicators or patterns are intentionally preserved to reflect **real-world data sparsity**
- Platform diversity is capped at 11 by the ATT&CK knowledge base
- All statistics were extracted programmatically to ensure reproducibility

---

## 8. Citation

If you use this dataset or structure, please cite **MITRE ATT&CK** and reference this repository accordingly.
