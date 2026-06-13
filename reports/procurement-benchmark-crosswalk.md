# Procurement Benchmark Crosswalk

This audit maps procurement source moments to the denominator used to compute them. It separates aggregate USAspending transaction-history moments from agency, award-type, and agency-by-award-type slices so validation does not compare unlike quantities.

## Benchmark Remapping

- Top-3 recipient concentration: bulk aggregate `0.1140`; agency range `0.0528-0.5130`; award-type range `0.0245-0.3659`; high-amount agency/award-type range `0.0286-0.7707`.
- The old top-contractor benchmark `0.25-0.40` is retained as a high-concentration slice diagnostic, not as the configured-agency aggregate denominator.
- Modification incidence: action-row `0.1705`; distinct-award `0.1067`; amount-weighted `0.5964`.
- The old ex-post modification benchmark `0.01-0.05` is retained as a delta/stress-screen concept, not as an absolute transaction-incidence range.

## Selected Crosswalk Rows

| Dimension | Value | Rows | Awards | Amount | Top-3 Recipients | Modified Actions | Modified Awards | Amount-Wtd Mod. | Recipient Class | Modification Class |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| all | all | 6449101 | 5740062 | 774172.8475 | 0.1141 | 0.1705 | 0.1067 | 0.5964 | below old top-contractor range | above old absolute range |
| agency | Department of Defense | 4420300 | 4050899 | 484953.2906 | 0.1740 | 0.1337 | 0.0845 | 0.5774 | below old top-contractor range | above old absolute range |
| agency | Department of Veterans Affairs | 126203 | 95645 | 72143.3704 | 0.5130 | 0.5316 | 0.4600 | 0.2695 | above old top-contractor range | above old absolute range |
| agency | Department of Energy | 11725 | 5336 | 52490.7545 | 0.2996 | 0.8048 | 0.6801 | 0.9833 | inside old top-contractor range | above old absolute range |
| agency | Department of Health and Human Services | 66795 | 36047 | 45282.7394 | 0.1617 | 0.6708 | 0.6769 | 0.7052 | below old top-contractor range | above old absolute range |
| agency | General Services Administration | 1551824 | 1378065 | 29592.3785 | 0.1833 | 0.1372 | 0.0730 | 0.6960 | below old top-contractor range | above old absolute range |
| agency | Department of Homeland Security | 60805 | 39256 | 27869.5348 | 0.1014 | 0.6738 | 0.6334 | 0.6669 | below old top-contractor range | above old absolute range |
| agency | National Aeronautics and Space Administration | 23156 | 9938 | 21071.9242 | 0.2792 | 0.7731 | 0.5899 | 0.9339 | inside old top-contractor range | above old absolute range |
| agency | Department of Agriculture | 75830 | 54273 | 12693.1987 | 0.0528 | 0.4848 | 0.4195 | 0.2709 | below old top-contractor range | above old absolute range |
| agency | Department of Transportation | 33687 | 17884 | 10321.8402 | 0.1573 | 0.7640 | 0.6752 | 0.6836 | below old top-contractor range | above old absolute range |
| agency | Department of the Interior | 48802 | 34267 | 9271.9122 | 0.1024 | 0.6460 | 0.6004 | 0.4727 | below old top-contractor range | above old absolute range |
| agency | Department of Commerce | 16593 | 12003 | 5905.6174 | 0.1499 | 0.6271 | 0.5667 | 0.6051 | below old top-contractor range | above old absolute range |
| agency | Environmental Protection Agency | 13381 | 6578 | 2576.2866 | 0.1749 | 0.8186 | 0.7563 | 0.5282 | below old top-contractor range | above old absolute range |
| awardType | DELIVERY ORDER | 4447816 | 4141572 | 429612.7033 | 0.1197 | 0.1050 | 0.0629 | 0.4838 | below old top-contractor range | above old absolute range |
| awardType | DEFINITIVE CONTRACT | 141449 | 63159 | 285112.5616 | 0.1709 | 0.8412 | 0.7490 | 0.7775 | below old top-contractor range | above old absolute range |
| awardType | BPA CALL | 868765 | 796868 | 24184.0573 | 0.1751 | 0.1167 | 0.0992 | 0.5198 | below old top-contractor range | above old absolute range |
| awardType | PURCHASE ORDER | 747371 | 646047 | 19220.8247 | 0.0245 | 0.2575 | 0.2295 | 0.2585 | below old top-contractor range | above old absolute range |
| awardType | contract | 243700 | 93513 | 16042.7007 | 0.3659 | 0.9015 | 0.8341 | 0.9120 | inside old top-contractor range | above old absolute range |
| agencyAwardType | Department of Health and Human Services\|\|contract | 5145 | 3506 | 7617.0684 | 0.7707 | 0.8595 | 0.8334 | 0.8369 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Energy\|\|contract | 637 | 281 | 1666.1869 | 0.7200 | 0.8681 | 0.8078 | 0.9996 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Energy\|\|BPA CALL | 2529 | 1070 | 1104.9979 | 0.6438 | 0.8284 | 0.7710 | 0.7818 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Veterans Affairs\|\|DELIVERY ORDER | 49714 | 39196 | 63262.2299 | 0.5850 | 0.4848 | 0.4283 | 0.2559 | above old top-contractor range | above old absolute range |
| agencyAwardType | National Aeronautics and Space Administration\|\|DELIVERY ORDER | 9893 | 4235 | 6253.2206 | 0.5598 | 0.7898 | 0.6165 | 0.8987 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Energy\|\|DELIVERY ORDER | 4687 | 2324 | 4378.5199 | 0.4808 | 0.7802 | 0.6437 | 0.9179 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Commerce\|\|DEFINITIVE CONTRACT | 1282 | 751 | 1785.0704 | 0.4635 | 0.7933 | 0.7124 | 0.6782 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Defense\|\|BPA CALL | 56302 | 47086 | 5960.6516 | 0.4231 | 0.3272 | 0.2710 | 0.3971 | above old top-contractor range | above old absolute range |
| agencyAwardType | Department of Homeland Security\|\|BPA CALL | 9080 | 6000 | 5288.0012 | 0.3763 | 0.6496 | 0.6375 | 0.6776 | inside old top-contractor range | above old absolute range |
| agencyAwardType | National Aeronautics and Space Administration\|\|contract | 3397 | 806 | 5291.5210 | 0.3542 | 0.9547 | 0.9045 | 0.9971 | inside old top-contractor range | above old absolute range |
| agencyAwardType | Department of Energy\|\|DEFINITIVE CONTRACT | 2603 | 627 | 45268.3284 | 0.3474 | 0.9370 | 0.8549 | 0.9950 | inside old top-contractor range | above old absolute range |
| agencyAwardType | National Aeronautics and Space Administration\|\|DEFINITIVE CONTRACT | 4523 | 1244 | 9075.9800 | 0.3209 | 0.9346 | 0.8199 | 0.9471 | inside old top-contractor range | above old absolute range |
| agencyAwardType | General Services Administration\|\|DEFINITIVE CONTRACT | 5515 | 3395 | 4167.8648 | 0.3101 | 0.5458 | 0.3417 | 0.5551 | inside old top-contractor range | above old absolute range |
| agencyAwardType | Department of Veterans Affairs\|\|BPA CALL | 8398 | 6829 | 1644.7019 | 0.3004 | 0.4830 | 0.4739 | 0.4230 | inside old top-contractor range | above old absolute range |
| agencyAwardType | Department of Transportation\|\|DEFINITIVE CONTRACT | 5160 | 2152 | 2415.6486 | 0.2621 | 0.8688 | 0.8039 | 0.6871 | inside old top-contractor range | above old absolute range |
| agencyAwardType | General Services Administration\|\|DELIVERY ORDER | 502704 | 483657 | 21110.2091 | 0.2525 | 0.0541 | 0.0380 | 0.7619 | inside old top-contractor range | award-share inside old range |
