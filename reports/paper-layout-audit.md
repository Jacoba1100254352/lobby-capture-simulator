# Paper Layout Audit

This audit checks generated PDFs for sparse float pages, large whitespace gaps, and figure or table pages without enough surrounding readable text. It is a regression guard, not a substitute for final visual inspection.

- Pages checked: `31`
- Failures: `0`

| PDF | Page | Blocks | Chars | Coverage | Largest gap | Float label | Status | Note |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| paper/main.pdf | 1 | 39 | 2531 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/main.pdf | 2 | 43 | 3237 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 3 | 123 | 3195 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 4 | 134 | 3509 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 5 | 150 | 3797 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 6 | 47 | 1841 | 0.854 | 0.055 | yes | pass | layout density acceptable |
| paper/main.pdf | 7 | 161 | 2993 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 8 | 89 | 1909 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 9 | 85 | 1744 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 10 | 56 | 2370 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 11 | 127 | 3408 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 12 | 55 | 1979 | 0.854 | 0.055 | yes | pass | layout density acceptable |
| paper/main.pdf | 13 | 44 | 2697 | 0.854 | 0.088 | no | pass | layout density acceptable |
| paper/main.pdf | 14 | 90 | 2500 | 0.857 | 0.053 | no | pass | references/declarations page |
| paper/main.pdf | 15 | 89 | 2231 | 0.854 | 0.146 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 1 | 26 | 1402 | 0.876 | 0.369 | no | pass | title/front-matter page |
| paper/regulation-governance-wiley.pdf | 2 | 149 | 4719 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 3 | 146 | 4500 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 4 | 123 | 4941 | 0.942 | 0.044 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 5 | 163 | 2611 | 0.939 | 0.072 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 6 | 144 | 2662 | 0.939 | 0.049 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 7 | 127 | 1866 | 0.939 | 0.064 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 8 | 97 | 2153 | 0.939 | 0.078 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 9 | 140 | 4724 | 0.939 | 0.043 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 10 | 81 | 2457 | 0.942 | 0.064 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 11 | 64 | 4213 | 0.943 | 0.043 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 12 | 105 | 4218 | 0.942 | 0.186 | no | pass | references/declarations page |
| paper/supplement.pdf | 1 | 33 | 1930 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/supplement.pdf | 2 | 71 | 1804 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/supplement.pdf | 3 | 54 | 1994 | 0.857 | 0.053 | yes | pass | references/declarations page |
| paper/supplement.pdf | 4 | 22 | 660 | 0.858 | 0.535 | no | pass | layout density acceptable |
