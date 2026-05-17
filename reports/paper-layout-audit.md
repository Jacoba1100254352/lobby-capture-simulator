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
| paper/main.pdf | 5 | 62 | 3602 | 0.854 | 0.065 | yes | pass | layout density acceptable |
| paper/main.pdf | 6 | 209 | 2978 | 0.795 | 0.129 | yes | pass | layout density acceptable |
| paper/main.pdf | 7 | 51 | 1638 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 8 | 97 | 1900 | 0.847 | 0.079 | yes | pass | layout density acceptable |
| paper/main.pdf | 9 | 82 | 1776 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 10 | 90 | 1789 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 11 | 133 | 3943 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 12 | 78 | 3464 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 13 | 56 | 2119 | 0.847 | 0.063 | yes | pass | layout density acceptable |
| paper/main.pdf | 14 | 55 | 2539 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 15 | 91 | 2471 | 0.854 | 0.055 | no | pass | references/declarations page |
| paper/main.pdf | 16 | 100 | 2354 | 0.854 | 0.100 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 1 | 26 | 1402 | 0.876 | 0.369 | no | pass | title/front-matter page |
| paper/regulation-governance-wiley.pdf | 2 | 149 | 4719 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 3 | 146 | 4500 | 0.943 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 4 | 123 | 5017 | 0.942 | 0.043 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 5 | 282 | 4252 | 0.939 | 0.067 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 6 | 134 | 2102 | 0.933 | 0.052 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 7 | 109 | 2548 | 0.933 | 0.044 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 8 | 133 | 2027 | 0.933 | 0.059 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 9 | 61 | 3328 | 0.933 | 0.057 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 10 | 115 | 4441 | 0.939 | 0.067 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 11 | 63 | 2864 | 0.933 | 0.044 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 12 | 93 | 3985 | 0.942 | 0.043 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 13 | 58 | 2389 | 0.942 | 0.522 | no | pass | references/declarations page |
| paper/supplement.pdf | 1 | 33 | 1931 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/supplement.pdf | 2 | 71 | 1804 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/supplement.pdf | 3 | 49 | 2178 | 0.857 | 0.053 | no | pass | references/declarations page |
| paper/supplement.pdf | 4 | 57 | 2502 | 0.858 | 0.052 | yes | pass | references/declarations page |
