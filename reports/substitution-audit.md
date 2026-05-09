# Substitution Audit

This audit treats lower observed capture as insufficient when hidden influence, hidden capture, total distortion, or substitution failure risk rises. Network opacity, venue shifting, and channel-network load remain diagnostic columns, but pure movement across channels without higher hidden influence or distortion is classified as a substitution tradeoff. It is a diagnostic over synthetic simulation reports, not an empirical causal claim.

- Possible failure: `22`
- Substitution tradeoff: `20`
- Worse total distortion: `2`
- Improved: `37`
- No material tradeoff: `3`

## Flagged Rows

| Report | Scenario | Status | Capture delta | Hidden delta | Hidden capture delta | Total distortion delta | Risk delta | Visible spend delta | Network opacity delta | Venue delta | Interm. load delta | Procurement delta | Revolving delta | Comment delta | Intermediary | Dark money | Defensive | Admin |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lobby-capture-ablation.csv | No beneficial-owner disclosure | possible_failure | -0.0813 | 0.0687 | 0.0144 | -0.0021 | 0.0324 | -0.0587 | 0.1700 | 0.0699 | -0.0055 | 0.0188 | 0.0347 | -0.0111 | 0.0991 | 0.1669 | 0.4452 | 0.4780 |
| lobby-capture-ablation.csv | No anti-astroturf authentication | substitution_tradeoff | -0.3556 | -0.0854 | -0.0453 | -0.0982 | -0.0616 | -0.0383 | 0.0282 | -0.0454 | 0.0140 | 0.0020 | -0.0072 | 0.0603 | 0.0902 | 0.2176 | 0.4808 | 0.4754 |
| lobby-capture-ablation.csv | No public advocate or blind review | substitution_tradeoff | -0.1672 | -0.0796 | -0.0389 | -0.0464 | -0.0573 | -0.0386 | 0.0297 | -0.0421 | 0.0146 | 0.1610 | -0.0071 | -0.0053 | 0.0907 | 0.2214 | 0.4564 | 0.4527 |
| lobby-capture-campaign.csv | Low-salience technical rulemaking | substitution_tradeoff | 0.1104 | 0.0618 | 0.0218 | 0.0487 | 0.0364 | -0.2151 | 0.0705 | 0.0361 | 0.0922 | -0.1059 | -0.0842 | 0.3313 | 0.1001 | 0.1206 | 0.0000 | 0.0966 |
| lobby-capture-campaign.csv | Campaign finance dominant | worse_total_distortion | 0.1085 | 0.0756 | 0.0289 | 0.0300 | 0.0412 | 0.2541 | 0.0560 | 0.0313 | -0.0080 | -0.1480 | -0.0576 | -0.1913 | 0.0800 | 0.1000 | 0.0000 | 0.0773 |
| lobby-capture-campaign.csv | Dark money dominant | substitution_tradeoff | 0.0063 | 0.3496 | 0.1192 | 0.0782 | 0.1760 | -0.0460 | 0.1925 | 0.2262 | 0.0800 | -0.0263 | -0.0090 | 0.0515 | 0.0880 | 0.1865 | 0.4305 | 0.0820 |
| lobby-capture-campaign.csv | Revolving-door dominant | substitution_tradeoff | 0.1100 | 0.0645 | 0.0242 | 0.0501 | 0.0398 | -0.1174 | 0.0920 | 0.0751 | -0.0155 | 0.0237 | 0.1536 | 0.0185 | 0.1038 | 0.1029 | 0.0000 | 0.0848 |
| lobby-capture-campaign.csv | Think-tank and association intermediaries | possible_failure | -0.0593 | 0.3030 | 0.0956 | 0.0394 | 0.1184 | -0.0413 | -0.1139 | 0.1165 | 0.0890 | -0.1456 | -0.0949 | 0.2869 | 0.0866 | 0.2084 | 0.4558 | 0.2875 |
| lobby-capture-campaign.csv | Real-time transparency | possible_failure | -0.2103 | 0.0930 | 0.0230 | -0.0424 | 0.0200 | -0.0470 | -0.1831 | 0.0203 | 0.0798 | -0.0522 | -0.0539 | 0.0248 | 0.0906 | 0.2019 | 0.2730 | 0.2779 |
| lobby-capture-campaign.csv | Democracy vouchers | substitution_tradeoff | -0.6250 | 0.0018 | -0.0085 | -0.1816 | -0.0010 | -0.0840 | 0.0091 | 0.0454 | 0.0560 | -0.1277 | -0.0715 | -0.1913 | 0.0863 | 0.2007 | 0.6787 | 0.2584 |
| lobby-capture-campaign.csv | Cooling-off ban | substitution_tradeoff | 0.0769 | 0.1887 | 0.0634 | 0.0519 | 0.0834 | -0.0859 | -0.0671 | 0.0907 | 0.0907 | -0.1246 | -0.2997 | 0.0373 | 0.1200 | 0.2200 | 0.0000 | 0.3682 |
| lobby-capture-campaign.csv | Audit and sanctions | possible_failure | -0.4071 | 0.0538 | 0.0022 | -0.0891 | -0.0012 | -0.0229 | -0.0684 | 0.0052 | 0.0678 | -0.0711 | -0.0912 | 0.0126 | 0.0882 | 0.1770 | 0.3285 | 0.4135 |
| lobby-capture-campaign.csv | Hard lobbying budgets | possible_failure | -0.1506 | 0.2643 | 0.0797 | 0.0045 | 0.1073 | -0.0916 | -0.0971 | 0.1154 | 0.1009 | -0.0811 | -0.1703 | 0.0126 | 0.1044 | 0.2315 | 0.2741 | 0.4809 |
| lobby-capture-campaign.csv | Public-interest representation funds | possible_failure | -0.2265 | 0.1290 | 0.0365 | -0.0313 | 0.0518 | -0.0301 | -0.0412 | 0.0658 | 0.0845 | -0.2559 | -0.1211 | 0.2343 | 0.0875 | 0.2213 | 0.3107 | 0.3719 |
| lobby-capture-campaign.csv | Randomized audit and sanctions | possible_failure | -0.4793 | 0.1040 | 0.0152 | -0.0980 | 0.0194 | -0.0541 | -0.0676 | 0.0320 | 0.0732 | -0.0921 | -0.0884 | 0.0115 | 0.0904 | 0.1892 | 0.3299 | 0.4551 |
| lobby-capture-campaign.csv | Machine-readable meeting logs | possible_failure | -0.2381 | 0.1526 | 0.0374 | -0.0363 | 0.0403 | -0.0385 | -0.2133 | 0.0440 | 0.0948 | -0.1152 | -0.1041 | 0.0292 | 0.0928 | 0.2997 | 0.0000 | 0.3563 |
| lobby-capture-campaign.csv | Hard-budget substitution stress | possible_failure | -0.2250 | 0.3969 | 0.1300 | 0.0132 | 0.1705 | -0.0750 | -0.0497 | 0.1858 | 0.0819 | -0.0827 | -0.1487 | -0.0190 | 0.0931 | 0.1752 | 0.6101 | 0.4650 |
| lobby-capture-campaign.csv | Shadow lobbying maximum stress | possible_failure | -0.3634 | 0.3381 | 0.1266 | -0.0210 | 0.1507 | -0.0816 | -0.0606 | 0.1832 | 0.0510 | -0.0253 | -0.1362 | -0.0766 | 0.0975 | 0.1976 | 0.4778 | 0.4476 |
| lobby-capture-campaign.csv | Advisory lobbying substitution | possible_failure | -0.3265 | 0.2964 | 0.1021 | -0.0124 | 0.1306 | -0.0638 | -0.0343 | 0.1604 | 0.0567 | -0.1531 | -0.3277 | 0.1088 | 0.0905 | 0.1390 | 0.7187 | 0.4237 |
| lobby-capture-campaign.csv | Procurement venue-shift stress | possible_failure | -0.3562 | 0.3220 | 0.1147 | -0.0105 | 0.1360 | -0.1299 | -0.0863 | 0.1611 | 0.0110 | 0.2613 | -0.0768 | -0.1913 | 0.1035 | 0.1639 | 0.2014 | 0.5134 |
| lobby-capture-campaign.csv | Outside-spending disclosure evasion | possible_failure | -0.3468 | 0.2867 | 0.0935 | -0.0475 | 0.1226 | -0.1109 | -0.0265 | 0.1629 | 0.0587 | -0.1447 | -0.0847 | -0.1051 | 0.0922 | 0.2872 | 0.3888 | 0.4734 |
| lobby-capture-campaign.csv | Enforced cooling-off periods | possible_failure | -0.1178 | 0.2165 | 0.0629 | 0.0078 | 0.0847 | -0.0859 | -0.0998 | 0.0897 | 0.0906 | -0.1331 | -0.3294 | 0.0294 | 0.1200 | 0.2200 | 0.0000 | 0.4581 |
| lobby-capture-campaign.csv | Comment-authenticity rules | possible_failure | -0.3234 | 0.1678 | 0.0515 | -0.0435 | 0.0664 | -0.0710 | -0.0617 | 0.0701 | 0.0634 | -0.2409 | -0.1185 | 0.0691 | 0.1001 | 0.1654 | 0.4301 | 0.4773 |
| lobby-capture-campaign.csv | Public advocate office | possible_failure | -0.2187 | 0.1493 | 0.0436 | -0.0272 | 0.0580 | -0.1553 | -0.0668 | 0.0362 | 0.0664 | -0.2612 | -0.1018 | 0.1981 | 0.0924 | 0.1162 | 0.3376 | 0.4133 |
| lobby-capture-campaign.csv | Procurement firewalls | possible_failure | -0.2925 | 0.1415 | 0.0487 | -0.0202 | 0.0452 | -0.1570 | -0.1749 | 0.0485 | -0.0413 | 0.3580 | 0.0254 | -0.1913 | 0.1053 | 0.0510 | 0.1486 | 0.5300 |
| lobby-capture-campaign.csv | Venue-shifting detection | possible_failure | -0.5340 | 0.1898 | 0.0479 | -0.1072 | 0.0575 | -0.0336 | -0.2125 | 0.0474 | 0.0705 | -0.1497 | -0.1836 | -0.0471 | 0.0954 | 0.1542 | 0.4538 | 0.5145 |
| lobby-capture-campaign.csv | Full anti-capture bundle | possible_failure | -0.8665 | 0.0589 | -0.0017 | -0.2242 | -0.0047 | -0.0513 | -0.2715 | -0.0163 | 0.0621 | -0.1869 | -0.2753 | -0.0603 | 0.0932 | 0.1469 | 0.6020 | 0.4958 |
| lobby-capture-campaign.csv | Anti-capture bundle with evasion | possible_failure | -0.4668 | 0.3301 | 0.0915 | -0.0883 | 0.1277 | -0.0426 | -0.1773 | 0.1318 | 0.0596 | -0.1916 | -0.2537 | -0.0628 | 0.0927 | 0.1460 | 0.5744 | 0.5338 |
| lobby-capture-campaign.csv | Reform threat mobilization | possible_failure | -0.3781 | 0.0743 | 0.0168 | -0.0996 | 0.0161 | -0.0660 | -0.1596 | 0.0393 | 0.0578 | -0.0639 | -0.0580 | -0.0191 | 0.0872 | 0.1801 | 0.5724 | 0.2555 |
| lobby-capture-interactions.csv | Interaction enforcement 0.10 disclosure 0.10 | substitution_tradeoff | 0.2280 | -0.2059 | -0.0429 | 0.0458 | -0.0433 | -0.0839 | 0.2805 | -0.0167 | -0.0091 | -0.0085 | -0.0201 | -0.0061 | 0.0874 | 0.1137 | 0.6261 | 0.4761 |
| lobby-capture-interactions.csv | Interaction enforcement 0.10 disclosure 0.80 | substitution_tradeoff | 0.0806 | -0.2667 | -0.0740 | -0.0175 | -0.0995 | -0.0461 | 0.0256 | -0.0811 | 0.0089 | -0.0011 | -0.0189 | 0.0031 | 0.1020 | 0.1867 | 0.4148 | 0.4976 |
| lobby-capture-interactions.csv | Interaction enforcement 0.80 disclosure 0.10 | substitution_tradeoff | 0.0960 | -0.2455 | -0.0671 | -0.0030 | -0.0775 | -0.1064 | 0.2675 | -0.0580 | -0.0096 | -0.0072 | -0.0180 | -0.0182 | 0.0902 | 0.1151 | 0.4740 | 0.5235 |
| lobby-capture-interactions.csv | Interaction enforcement 1.25 disclosure 0.10 | substitution_tradeoff | -0.1527 | -0.2793 | -0.0911 | -0.0677 | -0.1053 | -0.0966 | 0.2625 | -0.0847 | -0.0105 | -0.0039 | -0.0195 | -0.0126 | 0.0893 | 0.1236 | 0.5293 | 0.6508 |
| lobby-capture-portfolio.csv | Portfolio: balanced compliance core | substitution_tradeoff | 0.0077 | -0.2824 | -0.0872 | -0.0332 | -0.1229 | -0.0223 | 0.0562 | -0.0979 | 0.0139 | 0.0747 | 0.0317 | 0.0403 | 0.0905 | 0.2115 | 0.4629 | 0.4378 |
| lobby-capture-portfolio.csv | Portfolio: electoral substitution shield | substitution_tradeoff | 0.1212 | -0.2458 | -0.0714 | 0.0030 | -0.0975 | -0.0654 | 0.1276 | -0.0522 | 0.0223 | 0.1132 | 0.1718 | 0.0522 | 0.0908 | 0.2663 | 0.4585 | 0.4850 |
| lobby-capture-portfolio.csv | Portfolio: rulemaking integrity stack | substitution_tradeoff | 0.0371 | -0.2206 | -0.0643 | -0.0154 | -0.0883 | -0.0418 | 0.0963 | -0.0711 | 0.0112 | 0.0236 | 0.1969 | -0.0210 | 0.0999 | 0.1960 | 0.4361 | 0.5105 |
| lobby-capture-portfolio.csv | Portfolio: procurement hardening stack | substitution_tradeoff | -0.1225 | -0.2798 | -0.0904 | -0.0655 | -0.1263 | -0.0370 | 0.0346 | -0.1125 | 0.0085 | 0.0071 | 0.0282 | 0.0417 | 0.0992 | 0.1807 | 0.4773 | 0.5684 |
| lobby-capture-portfolio.csv | Portfolio: countervailing representation stack | substitution_tradeoff | 0.0342 | -0.2783 | -0.0819 | -0.0254 | -0.1084 | -0.0316 | 0.1335 | -0.0864 | 0.0053 | 0.0169 | 0.2145 | 0.0166 | 0.1020 | 0.1704 | 0.4352 | 0.4149 |
| lobby-capture-portfolio.csv | Portfolio: high-deterrence enforcement stack | substitution_tradeoff | -0.1094 | -0.2153 | -0.0712 | -0.0518 | -0.0963 | -0.0397 | 0.0555 | -0.0767 | 0.0107 | 0.0261 | -0.0270 | 0.0224 | 0.0980 | 0.1886 | 0.4882 | 0.6195 |
| lobby-capture-sensitivity.csv | Sensitivity disclosure 0.10 | substitution_tradeoff | 0.0834 | 0.0270 | 0.0083 | 0.0358 | 0.0300 | -0.1056 | 0.3481 | 0.0503 | -0.0091 | 0.0012 | 0.0016 | -0.0152 | 0.0899 | 0.1209 | 0.4855 | 0.5378 |
| lobby-capture-sensitivity.csv | Sensitivity disclosure 0.35 | substitution_tradeoff | 0.0015 | 0.0097 | -0.0017 | 0.0115 | 0.0120 | -0.0444 | 0.2702 | 0.0384 | 0.0064 | 0.0080 | 0.0044 | -0.0082 | 0.1022 | 0.1711 | 0.4405 | 0.5340 |
| lobby-capture-sensitivity.csv | Sensitivity disclosure 0.80 | substitution_tradeoff | -0.2466 | -0.0445 | -0.0274 | -0.0679 | -0.0326 | -0.0436 | 0.0843 | -0.0245 | 0.0034 | -0.0056 | 0.0030 | -0.0076 | 0.0992 | 0.1676 | 0.5101 | 0.5121 |
| lobby-capture-sensitivity.csv | Sensitivity evasion 0.60 | possible_failure | -0.1714 | 0.0607 | 0.0066 | -0.0331 | 0.0128 | -0.0124 | 0.0319 | 0.0168 | 0.0033 | 0.0020 | 0.0006 | -0.0014 | 0.0961 | 0.1555 | 0.4682 | 0.5261 |
| lobby-capture-sensitivity.csv | Sensitivity evasion 0.90 | worse_total_distortion | 0.0672 | 0.2576 | 0.0770 | 0.0507 | 0.1055 | -0.0061 | 0.0827 | 0.1071 | -0.0023 | -0.0053 | 0.0214 | -0.0030 | 0.0951 | 0.1532 | 0.4646 | 0.5492 |
