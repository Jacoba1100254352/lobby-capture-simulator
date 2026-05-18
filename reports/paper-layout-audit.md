# Paper Layout Audit

This audit checks generated PDFs for sparse float pages, large whitespace gaps, and figure or table pages without enough surrounding readable text. It is a regression guard, not a substitute for final visual inspection.

- Pages checked: `36`
- Failures: `0`

| PDF | Page | Blocks | Chars | Coverage | Largest gap | Float label | Status | Note |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| paper/main.pdf | 1 | 41 | 2645 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/main.pdf | 2 | 42 | 3062 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 3 | 57 | 2673 | 0.848 | 0.130 | yes | pass | layout density acceptable |
| paper/main.pdf | 4 | 133 | 1931 | 0.674 | 0.235 | yes | pass | layout density acceptable |
| paper/main.pdf | 5 | 173 | 3570 | 0.857 | 0.053 | no | pass | layout density acceptable |
| paper/main.pdf | 6 | 100 | 3442 | 0.854 | 0.097 | no | pass | layout density acceptable |
| paper/main.pdf | 7 | 50 | 3875 | 0.857 | 0.053 | yes | pass | layout density acceptable |
| paper/main.pdf | 8 | 194 | 3074 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 9 | 52 | 2055 | 0.848 | 0.061 | yes | pass | layout density acceptable |
| paper/main.pdf | 10 | 186 | 2475 | 0.846 | 0.064 | yes | pass | layout density acceptable |
| paper/main.pdf | 11 | 84 | 1616 | 0.848 | 0.061 | yes | pass | layout density acceptable |
| paper/main.pdf | 12 | 99 | 2135 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 13 | 126 | 3453 | 0.852 | 0.058 | yes | pass | layout density acceptable |
| paper/main.pdf | 14 | 60 | 2457 | 0.848 | 0.061 | yes | pass | layout density acceptable |
| paper/main.pdf | 15 | 56 | 2646 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/main.pdf | 16 | 91 | 2471 | 0.854 | 0.055 | no | pass | references/declarations page |
| paper/main.pdf | 17 | 100 | 2354 | 0.854 | 0.100 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 1 | 25 | 1265 | 0.876 | 0.385 | no | pass | title/front-matter page |
| paper/regulation-governance-wiley.pdf | 2 | 54 | 4722 | 0.943 | 0.051 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 3 | 100 | 3198 | 0.934 | 0.129 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 4 | 160 | 4671 | 0.939 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 5 | 130 | 4857 | 0.924 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 6 | 134 | 4297 | 0.939 | 0.080 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 7 | 125 | 2849 | 0.939 | 0.047 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 8 | 140 | 2930 | 0.939 | 0.076 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 9 | 140 | 2160 | 0.939 | 0.048 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 10 | 103 | 2427 | 0.939 | 0.071 | yes | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 11 | 134 | 4693 | 0.939 | 0.043 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 12 | 71 | 2900 | 0.934 | 0.088 | no | pass | layout density acceptable |
| paper/regulation-governance-wiley.pdf | 13 | 83 | 4012 | 0.943 | 0.043 | no | pass | references/declarations page |
| paper/regulation-governance-wiley.pdf | 14 | 32 | 1628 | 0.942 | 0.650 | no | pass | references/declarations page |
| paper/supplement.pdf | 1 | 33 | 1930 | 0.805 | 0.105 | no | pass | title/front-matter page |
| paper/supplement.pdf | 2 | 64 | 1693 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/supplement.pdf | 3 | 54 | 2151 | 0.854 | 0.055 | no | pass | layout density acceptable |
| paper/supplement.pdf | 4 | 55 | 2629 | 0.858 | 0.052 | yes | pass | references/declarations page |
| paper/supplement.pdf | 5 | 24 | 1483 | 0.858 | 0.466 | no | pass | references/declarations page |
