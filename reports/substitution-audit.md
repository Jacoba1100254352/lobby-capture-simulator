# Substitution Audit

This audit treats lower observed capture as insufficient when hidden influence, hidden capture, total distortion, or substitution failure risk rises. It is a diagnostic over synthetic simulation reports, not an empirical causal claim.

- Possible failure: `16`
- Substitution tradeoff: `4`
- Worse total distortion: `1`
- Improved: `46`
- No material tradeoff: `3`

## Flagged Rows

| Report | Scenario | Status | Capture delta | Hidden delta | Hidden capture delta | Total distortion delta | Risk delta | Visible spend delta | Intermediary | Dark money | Defensive | Admin |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lobby-capture-ablation.csv | No beneficial-owner disclosure | possible_failure | -0.1300 | 0.0577 | 0.0075 | -0.0235 | 0.0107 | -0.0411 | 0.0992 | 0.1843 | 0.4746 | 0.4411 |
| lobby-capture-campaign.csv | Low-salience technical rulemaking | substitution_tradeoff | 0.1657 | 0.0574 | 0.0219 | 0.0583 | 0.0301 | -0.2144 | 0.1002 | 0.1209 | 0.0000 | 0.0738 |
| lobby-capture-campaign.csv | Campaign finance dominant | worse_total_distortion | 0.0682 | 0.0707 | 0.0270 | 0.0229 | 0.0356 | 0.2544 | 0.0800 | 0.1000 | 0.0000 | 0.0733 |
| lobby-capture-campaign.csv | Dark money dominant | substitution_tradeoff | 0.0625 | 0.2771 | 0.0977 | 0.0633 | 0.1268 | -0.0411 | 0.0871 | 0.1860 | 0.4189 | 0.0697 |
| lobby-capture-campaign.csv | Revolving-door dominant | substitution_tradeoff | 0.1657 | 0.0563 | 0.0229 | 0.0557 | 0.0282 | -0.1682 | 0.1095 | 0.0432 | 0.0000 | 0.0761 |
| lobby-capture-campaign.csv | Think-tank and association intermediaries | substitution_tradeoff | -0.0043 | 0.3233 | 0.1150 | 0.0674 | 0.1538 | -0.0393 | 0.0866 | 0.2073 | 0.4535 | 0.2522 |
| lobby-capture-campaign.csv | Real-time transparency | possible_failure | -0.2350 | 0.1122 | 0.0378 | -0.0327 | 0.0602 | -0.0410 | 0.0898 | 0.2089 | 0.2817 | 0.2391 |
| lobby-capture-campaign.csv | Cooling-off ban | possible_failure | -0.1009 | 0.1521 | 0.0518 | 0.0123 | 0.0774 | -0.0856 | 0.1200 | 0.2200 | 0.0000 | 0.3336 |
| lobby-capture-campaign.csv | Audit and sanctions | possible_failure | -0.5359 | 0.0731 | 0.0114 | -0.1078 | 0.0247 | -0.0189 | 0.0878 | 0.1909 | 0.3420 | 0.3671 |
| lobby-capture-campaign.csv | Hard lobbying budgets | possible_failure | -0.2684 | 0.2177 | 0.0698 | -0.0218 | 0.1070 | -0.0888 | 0.1040 | 0.2237 | 0.2991 | 0.4345 |
| lobby-capture-campaign.csv | Public-interest representation funds | possible_failure | -0.4006 | 0.1401 | 0.0413 | -0.0568 | 0.0688 | -0.0550 | 0.0889 | 0.2403 | 0.3417 | 0.3346 |
| lobby-capture-campaign.csv | Randomized audit and sanctions | possible_failure | -0.5728 | 0.1287 | 0.0276 | -0.1070 | 0.0505 | -0.0351 | 0.0882 | 0.2019 | 0.3524 | 0.4088 |
| lobby-capture-campaign.csv | Machine-readable meeting logs | possible_failure | -0.2353 | 0.1818 | 0.0600 | -0.0130 | 0.0950 | -0.0567 | 0.0941 | 0.3170 | 0.0000 | 0.3151 |
| lobby-capture-campaign.csv | Enforced cooling-off periods | possible_failure | -0.3531 | 0.1938 | 0.0569 | -0.0383 | 0.0925 | -0.0856 | 0.1200 | 0.2200 | 0.0000 | 0.4038 |
| lobby-capture-campaign.csv | Comment-authenticity rules | possible_failure | -0.3115 | 0.1819 | 0.0627 | -0.0258 | 0.0884 | -0.0703 | 0.0996 | 0.1638 | 0.4232 | 0.4549 |
| lobby-capture-campaign.csv | Public advocate office | possible_failure | -0.3778 | 0.1569 | 0.0477 | -0.0475 | 0.0766 | -0.1579 | 0.0928 | 0.1164 | 0.3367 | 0.3779 |
| lobby-capture-campaign.csv | Procurement firewalls | possible_failure | -0.3725 | 0.1008 | 0.0349 | -0.0531 | 0.0463 | -0.0781 | 0.1100 | 0.1926 | 0.2280 | 0.4815 |
| lobby-capture-campaign.csv | Venue-shifting detection | possible_failure | -0.4740 | 0.2184 | 0.0689 | -0.0710 | 0.1055 | -0.0320 | 0.0958 | 0.1555 | 0.4356 | 0.4905 |
| lobby-capture-campaign.csv | Full anti-capture bundle | possible_failure | -0.8178 | 0.0723 | 0.0100 | -0.1918 | 0.0359 | -0.0522 | 0.0929 | 0.1462 | 0.6141 | 0.4733 |
| lobby-capture-campaign.csv | Anti-capture bundle with evasion | possible_failure | -0.4590 | 0.3287 | 0.0990 | -0.0714 | 0.1518 | -0.0426 | 0.0933 | 0.1476 | 0.5586 | 0.5090 |
| lobby-capture-campaign.csv | Reform threat mobilization | possible_failure | -0.3806 | 0.0890 | 0.0274 | -0.0863 | 0.0442 | -0.0645 | 0.0844 | 0.1554 | 0.7392 | 0.2286 |
