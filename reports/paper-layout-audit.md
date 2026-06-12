# Paper Layout Audit

This audit checks generated PDFs for sparse float pages, large whitespace gaps, and figure or table pages without enough surrounding readable text. It is a regression guard, not a substitute for final visual inspection.

- Pages checked: `42`
- Failures: `0`

| PDF | Page | Blocks | Chars | Coverage | Largest gap | Float label | Status | Note |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 1 | 41 | 2724 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 2 | 42 | 3055 | 0.857 | 0.053 | no | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 3 | 59 | 2455 | 0.847 | 0.075 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 4 | 211 | 3049 | 0.850 | 0.059 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 5 | 128 | 3637 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 6 | 207 | 3295 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 7 | 75 | 3711 | 0.854 | 0.055 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 8 | 116 | 3889 | 0.854 | 0.055 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 9 | 169 | 2679 | 0.854 | 0.055 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 10 | 108 | 1928 | 0.849 | 0.060 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 11 | 155 | 2100 | 0.849 | 0.090 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 12 | 106 | 1725 | 0.848 | 0.066 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 13 | 78 | 1490 | 0.848 | 0.126 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 14 | 93 | 1495 | 0.848 | 0.130 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 15 | 138 | 3443 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 16 | 57 | 3451 | 0.857 | 0.053 | no | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 17 | 51 | 2028 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 18 | 63 | 2471 | 0.854 | 0.055 | no | pass | references/declarations page |
| paper/strategic-channel-substitution-regulatory-capture.pdf | 19 | 26 | 885 | 0.854 | 0.567 | no | pass | short terminal references/declarations page |
| paper/regulation-governance-wiley.pdf | 1 | 25 | 1253 | 0.876 | 0.385 | no | pass | title/front-matter page |
| paper/regulation-governance-wiley.pdf | 2 | 55 | 4904 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 3 | 58 | 2719 | 0.933 | 0.101 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 4 | 203 | 3497 | 0.939 | 0.047 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 5 | 165 | 5175 | 0.942 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 6 | 128 | 5135 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 7 | 115 | 4213 | 0.939 | 0.195 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 8 | 237 | 3670 | 0.939 | 0.063 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 9 | 116 | 1514 | 0.935 | 0.071 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 10 | 189 | 2464 | 0.934 | 0.084 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 11 | 136 | 2258 | 0.934 | 0.056 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 12 | 153 | 2804 | 0.934 | 0.055 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 13 | 64 | 4907 | 0.943 | 0.055 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 14 | 85 | 4041 | 0.943 | 0.043 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 15 | 30 | 1599 | 0.942 | 0.650 | no | pass | references/declarations page |
| paper/supplement.pdf | 1 | 37 | 2063 | 0.820 | 0.097 | no | pass | title/front-matter page |
| paper/supplement.pdf | 2 | 57 | 2834 | 0.872 | 0.046 | no | pass | layout density acceptable |
| paper/supplement.pdf | 3 | 233 | 2508 | 0.873 | 0.051 | yes | pass | layout density acceptable |
| paper/supplement.pdf | 4 | 82 | 2866 | 0.838 | 0.079 | yes | pass | layout density acceptable |
| paper/supplement.pdf | 5 | 83 | 2407 | 0.872 | 0.045 | yes | pass | layout density acceptable |
| paper/supplement.pdf | 6 | 54 | 3691 | 0.870 | 0.048 | yes | pass | layout density acceptable |
| paper/supplement.pdf | 7 | 101 | 3083 | 0.870 | 0.048 | yes | pass | references/declarations page |
| paper/supplement.pdf | 8 | 60 | 2649 | 0.870 | 0.056 | yes | pass | references/declarations page |
