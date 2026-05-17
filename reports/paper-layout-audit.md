# Paper Layout Audit

This audit checks generated PDFs for sparse float pages, large whitespace gaps, and figure or table pages without enough surrounding readable text. It is a regression guard, not a substitute for final visual inspection.

- Pages checked: `33`
- Failures: `0`

| PDF | Page | Blocks | Chars | Coverage | Largest gap | Float label | Status | Note |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| paper/main.pdf | 1 | 39 | 2532 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/main.pdf | 2 | 43 | 3237 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 3 | 123 | 3195 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 4 | 134 | 3509 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 5 | 168 | 3839 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 6 | 46 | 1803 | 0.854 | 0.075 | yes | pass | layout density acceptable |
| paper/main.pdf | 7 | 138 | 2988 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 8 | 88 | 1712 | 0.847 | 0.110 | yes | pass | layout density acceptable |
| paper/main.pdf | 9 | 86 | 1814 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 10 | 52 | 2182 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 11 | 163 | 3339 | 0.852 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 12 | 47 | 3697 | 0.857 | 0.053 | no | pass | layout density acceptable |
| paper/main.pdf | 13 | 57 | 1991 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 14 | 68 | 2352 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 15 | 91 | 2516 | 0.854 | 0.055 | no | pass | references/declarations page |
| paper/main.pdf | 16 | 44 | 1079 | 0.854 | 0.504 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 1 | 26 | 1402 | 0.876 | 0.369 | no | pass | title/front-matter page |
| paper/regulation-governance-wiley.pdf | 2 | 149 | 4719 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 3 | 146 | 4500 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 4 | 123 | 4941 | 0.942 | 0.044 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 5 | 187 | 2836 | 0.939 | 0.052 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 6 | 147 | 2709 | 0.939 | 0.049 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 7 | 127 | 1866 | 0.939 | 0.064 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 8 | 97 | 2153 | 0.939 | 0.078 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 9 | 140 | 4706 | 0.939 | 0.074 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 10 | 108 | 4564 | 0.939 | 0.055 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 11 | 67 | 2596 | 0.933 | 0.074 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 12 | 95 | 4045 | 0.943 | 0.043 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 13 | 33 | 1253 | 0.942 | 0.714 | no | pass | references/declarations page |
| paper/supplement.pdf | 1 | 33 | 1931 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/supplement.pdf | 2 | 71 | 1804 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/supplement.pdf | 3 | 49 | 2178 | 0.857 | 0.053 | no | pass | references/declarations page |
| paper/supplement.pdf | 4 | 57 | 2501 | 0.858 | 0.052 | yes | pass | references/declarations page |
