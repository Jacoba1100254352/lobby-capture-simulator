# Substitution Audit

This audit treats lower observed capture as insufficient when hidden influence, hidden capture, total distortion, or substitution failure risk rises. It is a diagnostic over synthetic simulation reports, not an empirical causal claim.

- Possible failure: `16`
- Substitution tradeoff: `11`
- Worse total distortion: `17`
- Improved: `30`
- No material tradeoff: `4`

## Flagged Rows

| Report | Scenario | Status | Capture delta | Hidden delta | Hidden capture delta | Total distortion delta | Risk delta | Visible spend delta | Intermediary | Dark money | Defensive | Admin |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lobby-capture-ablation.csv | No beneficial-owner disclosure | possible_failure | -0.1131 | 0.0569 | 0.0084 | -0.0115 | 0.0232 | -0.0537 | 0.1000 | 0.1956 | 0.4349 | 0.4653 |
| lobby-capture-campaign.csv | Low-salience technical rulemaking | substitution_tradeoff | 0.1088 | 0.0573 | 0.0211 | 0.0488 | 0.0357 | -0.2157 | 0.1001 | 0.1206 | 0.0000 | 0.0930 |
| lobby-capture-campaign.csv | Campaign finance dominant | worse_total_distortion | 0.1059 | 0.0705 | 0.0280 | 0.0281 | 0.0407 | 0.2535 | 0.0800 | 0.1000 | 0.0000 | 0.0737 |
| lobby-capture-campaign.csv | Dark money dominant | substitution_tradeoff | 0.0034 | 0.2755 | 0.0967 | 0.0663 | 0.1477 | -0.0432 | 0.0868 | 0.1823 | 0.4416 | 0.0783 |
| lobby-capture-campaign.csv | Revolving-door dominant | substitution_tradeoff | 0.1084 | 0.0561 | 0.0221 | 0.0492 | 0.0369 | -0.1704 | 0.1096 | 0.0427 | 0.0000 | 0.0801 |
| lobby-capture-campaign.csv | Think-tank and association intermediaries | possible_failure | -0.0497 | 0.3220 | 0.1143 | 0.0596 | 0.1607 | -0.0390 | 0.0862 | 0.2019 | 0.4745 | 0.2661 |
| lobby-capture-campaign.csv | Real-time transparency | possible_failure | -0.1053 | 0.1082 | 0.0399 | -0.0073 | 0.0572 | -0.0278 | 0.0887 | 0.2095 | 0.2706 | 0.2600 |
| lobby-capture-campaign.csv | Cooling-off ban | substitution_tradeoff | 0.0753 | 0.1507 | 0.0569 | 0.0534 | 0.0830 | -0.0865 | 0.1200 | 0.2200 | 0.0000 | 0.3497 |
| lobby-capture-campaign.csv | Audit and sanctions | possible_failure | -0.3059 | 0.0735 | 0.0166 | -0.0564 | 0.0293 | -0.0172 | 0.0875 | 0.1899 | 0.3160 | 0.4082 |
| lobby-capture-campaign.csv | Hard lobbying budgets | possible_failure | -0.1106 | 0.2186 | 0.0765 | 0.0172 | 0.1168 | -0.0927 | 0.1049 | 0.2334 | 0.2610 | 0.4571 |
| lobby-capture-campaign.csv | Public-interest representation funds | possible_failure | -0.1519 | 0.1368 | 0.0477 | -0.0056 | 0.0756 | -0.0307 | 0.0874 | 0.2207 | 0.3125 | 0.3610 |
| lobby-capture-campaign.csv | Randomized audit and sanctions | possible_failure | -0.3650 | 0.1296 | 0.0337 | -0.0602 | 0.0574 | -0.0173 | 0.0872 | 0.1904 | 0.3240 | 0.4494 |
| lobby-capture-campaign.csv | Machine-readable meeting logs | worse_total_distortion | 0.0513 | 0.1798 | 0.0686 | 0.0481 | 0.0947 | 0.0043 | 0.0899 | 0.2592 | 0.0000 | 0.3443 |
| lobby-capture-campaign.csv | Enforced cooling-off periods | possible_failure | -0.0509 | 0.1909 | 0.0657 | 0.0301 | 0.0987 | -0.0865 | 0.1200 | 0.2200 | 0.0000 | 0.4450 |
| lobby-capture-campaign.csv | Comment-authenticity rules | possible_failure | -0.2434 | 0.1918 | 0.0701 | -0.0099 | 0.1019 | -0.0743 | 0.1038 | 0.1754 | 0.3451 | 0.4676 |
| lobby-capture-campaign.csv | Public advocate office | possible_failure | -0.1312 | 0.1641 | 0.0579 | 0.0042 | 0.0862 | -0.1634 | 0.0934 | 0.1167 | 0.2930 | 0.4041 |
| lobby-capture-campaign.csv | Procurement firewalls | possible_failure | -0.2934 | 0.0962 | 0.0375 | -0.0223 | 0.0447 | -0.0812 | 0.1129 | 0.2004 | 0.1664 | 0.5005 |
| lobby-capture-campaign.csv | Venue-shifting detection | possible_failure | -0.3687 | 0.2162 | 0.0735 | -0.0518 | 0.1068 | -0.0286 | 0.0951 | 0.1535 | 0.4345 | 0.5101 |
| lobby-capture-campaign.csv | Full anti-capture bundle | possible_failure | -0.7544 | 0.0709 | 0.0122 | -0.1873 | 0.0295 | -0.0515 | 0.0930 | 0.1464 | 0.6056 | 0.4869 |
| lobby-capture-campaign.csv | Anti-capture bundle with evasion | possible_failure | -0.4072 | 0.3278 | 0.1038 | -0.0605 | 0.1594 | -0.0383 | 0.0928 | 0.1465 | 0.5480 | 0.5244 |
| lobby-capture-campaign.csv | Reform threat mobilization | possible_failure | -0.3237 | 0.0909 | 0.0305 | -0.0735 | 0.0466 | -0.0633 | 0.0845 | 0.1576 | 0.7191 | 0.2411 |
| lobby-capture-interactions.csv | Interaction enforcement 0.10 disclosure 0.10 | substitution_tradeoff | 0.5960 | 0.1603 | 0.0684 | 0.1839 | 0.1060 | -0.0801 | 0.0865 | 0.1132 | 0.6156 | 0.4734 |
| lobby-capture-interactions.csv | Interaction enforcement 0.10 disclosure 0.80 | substitution_tradeoff | 0.5014 | 0.1469 | 0.0628 | 0.1487 | 0.0937 | -0.0500 | 0.1016 | 0.1863 | 0.4204 | 0.4823 |
| lobby-capture-interactions.csv | Interaction enforcement 0.10 disclosure 1.25 | worse_total_distortion | 0.3534 | 0.1376 | 0.0585 | 0.1097 | 0.0846 | -0.0051 | 0.0958 | 0.1550 | 0.4386 | 0.5971 |
| lobby-capture-interactions.csv | Interaction enforcement 0.80 disclosure 0.10 | substitution_tradeoff | 0.4607 | 0.1497 | 0.0566 | 0.1437 | 0.0924 | -0.1054 | 0.0901 | 0.1289 | 0.4731 | 0.5135 |
| lobby-capture-interactions.csv | Interaction enforcement 0.80 disclosure 0.80 | substitution_tradeoff | 0.2794 | 0.1296 | 0.0467 | 0.0900 | 0.0746 | -0.0460 | 0.0993 | 0.1728 | 0.4969 | 0.5091 |
| lobby-capture-interactions.csv | Interaction enforcement 0.80 disclosure 1.25 | worse_total_distortion | 0.1407 | 0.1187 | 0.0422 | 0.0534 | 0.0650 | -0.0179 | 0.0955 | 0.1536 | 0.5077 | 0.6136 |
| lobby-capture-interactions.csv | Interaction enforcement 1.25 disclosure 0.10 | substitution_tradeoff | 0.2254 | 0.1376 | 0.0427 | 0.0855 | 0.0786 | -0.0877 | 0.0883 | 0.1225 | 0.5208 | 0.6400 |
| lobby-capture-interactions.csv | Interaction enforcement 1.25 disclosure 0.80 | substitution_tradeoff | 0.1094 | 0.1290 | 0.0390 | 0.0524 | 0.0681 | -0.0449 | 0.0992 | 0.1693 | 0.5066 | 0.6226 |
| lobby-capture-interactions.csv | Interaction enforcement 1.25 disclosure 1.25 | substitution_tradeoff | -0.0013 | 0.1111 | 0.0330 | 0.0162 | 0.0549 | -0.0204 | 0.0949 | 0.1519 | 0.5359 | 0.6088 |
| lobby-capture-interactions.csv | Interaction public financing 0.35 evasion 0.45 | worse_total_distortion | 0.2627 | 0.1688 | 0.0588 | 0.0929 | 0.0891 | -0.0069 | 0.0956 | 0.1541 | 0.4581 | 0.5139 |
| lobby-capture-interactions.csv | Interaction public financing 0.35 evasion 0.90 | worse_total_distortion | 0.4694 | 0.4199 | 0.1485 | 0.1841 | 0.2117 | -0.0022 | 0.0951 | 0.1534 | 0.4433 | 0.5365 |
| lobby-capture-interactions.csv | Interaction public financing 0.80 evasion 0.45 | worse_total_distortion | 0.2174 | 0.1647 | 0.0563 | 0.0803 | 0.0879 | -0.0107 | 0.0950 | 0.1526 | 0.4877 | 0.5112 |
| lobby-capture-interactions.csv | Interaction public financing 0.80 evasion 0.90 | worse_total_distortion | 0.4640 | 0.4077 | 0.1459 | 0.1785 | 0.2082 | -0.0020 | 0.0940 | 0.1503 | 0.4742 | 0.5329 |
| lobby-capture-interactions.csv | Interaction public financing 1.25 evasion 0.45 | worse_total_distortion | 0.2087 | 0.1640 | 0.0561 | 0.0791 | 0.0889 | -0.0101 | 0.0947 | 0.1517 | 0.4937 | 0.6234 |
| lobby-capture-interactions.csv | Interaction public financing 1.25 evasion 0.90 | worse_total_distortion | 0.4614 | 0.4195 | 0.1489 | 0.1814 | 0.2157 | -0.0014 | 0.0942 | 0.1509 | 0.4648 | 0.6506 |
| lobby-capture-interactions.csv | Interaction cooling 0.10 strategy balanced | worse_total_distortion | 0.1627 | 0.1241 | 0.0412 | 0.0590 | 0.0650 | -0.0128 | 0.0951 | 0.1529 | 0.4935 | 0.5054 |
| lobby-capture-interactions.csv | Interaction cooling 0.10 strategy revolving-door | worse_total_distortion | 0.1540 | 0.1265 | 0.0414 | 0.0580 | 0.0662 | -0.0130 | 0.0957 | 0.1545 | 0.4778 | 0.5056 |
| lobby-capture-interactions.csv | Interaction cooling 0.80 strategy balanced | worse_total_distortion | 0.1500 | 0.1253 | 0.0418 | 0.0571 | 0.0667 | -0.0119 | 0.0949 | 0.1524 | 0.4947 | 0.5028 |
| lobby-capture-interactions.csv | Interaction cooling 0.80 strategy revolving-door | worse_total_distortion | 0.1527 | 0.1298 | 0.0433 | 0.0602 | 0.0692 | -0.0141 | 0.0960 | 0.1553 | 0.4742 | 0.5055 |
| lobby-capture-interactions.csv | Interaction cooling 1.25 strategy balanced | worse_total_distortion | 0.1180 | 0.1271 | 0.0414 | 0.0506 | 0.0682 | -0.0162 | 0.0951 | 0.1527 | 0.5101 | 0.6151 |
| lobby-capture-interactions.csv | Interaction cooling 1.25 strategy revolving-door | worse_total_distortion | 0.1127 | 0.1252 | 0.0405 | 0.0488 | 0.0671 | -0.0174 | 0.0951 | 0.1526 | 0.5161 | 0.6154 |
| lobby-capture-sensitivity.csv | Sensitivity evasion 0.60 | possible_failure | -0.1053 | 0.0943 | 0.0234 | -0.0058 | 0.0395 | -0.0074 | 0.0961 | 0.1559 | 0.4352 | 0.5225 |
| lobby-capture-sensitivity.csv | Sensitivity evasion 0.90 | worse_total_distortion | 0.0376 | 0.2751 | 0.0875 | 0.0544 | 0.1257 | -0.0005 | 0.0944 | 0.1515 | 0.4512 | 0.5360 |
