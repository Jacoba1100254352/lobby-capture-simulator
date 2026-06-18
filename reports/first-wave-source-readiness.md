# First-Wave Source Readiness

This audit maps the first-wave causal protocols to committed source products. It is a pre-estimation gate: source products can support protocol design, but no row clears calibrated policy-simulation claims or causal effect language. Candidate linkage rows from `reports/first-wave-linkage-candidates.md` and candidate-only seed files under `data/calibration/first-wave/` are manual-review worklists only; they do not satisfy adjudicated production source-product requirements.

## Summary

- Protocols audited: `4`
- Ready to estimate: `0`
- Partial source support: `3`
- Blocked by missing source products: `1`
- Policy-simulation status: `not_cleared`
- Source-product schema gate: `blocked_until_required_products_exist`

## Readiness Matrix

| Target | Source readiness | Source-product gate | Current source products | Missing source products | Blocking issue |
| --- | --- | --- | --- | --- | --- |
| substitution-elasticity | partial_source_support_not_estimation_ready | schema_gate_blocked (required=4; ready=1; candidateOnly=0; missing=3; schemaIssues=0) | LDA visible-lobbying rows=121; OpenFEC outside-spending rows=998; OpenFEC electoral-communication rows=268; Regulations.gov/Federal Register rows=200; USAspending action rows=28104; intermediary rows=1353; candidate cross-source actor keys=659; cross-venue keys=140; source systems=8; venues=6 | named reform-shock event file; canonical actor-issue-time spine across at least three venues; pre/post comparison groups for exposed and unaffected actors or jurisdictions | Public surfaces exist, but the committed snapshot does not yet define an event panel that can estimate substitution elasticity. |
| procurement-modification-causal-capture | blocked_by_sam_fps_crosswalk_and_overlays | schema_gate_blocked (required=4; ready=0; candidateOnly=0; missing=4; schemaIssues=0) | USAspending bulk transaction rows=6449101; USAspending action rows=28104; known PIID share=1; ex-post modification share=0.4222; single-bid share=0.2350 | SAM/FPDS action-history export or keyed pull; GAO protest overlay; SAM exclusion overlay; procurement firewall or integrity-control overlay | USAspending denominators are present, but representative SAM/FPDS coding and protest/exclusion/firewall overlays remain absent. |
| comment-authenticity-and-uptake-effect | partial_source_support_not_estimation_ready | schema_gate_blocked (required=3; ready=0; candidateOnly=0; missing=3; schemaIssues=0) | Regulations.gov/Federal Register rows=200; mean template share=0.4600; mean authentication share=0.3200; comment-flooding index=0.3072 | comment-body corpus; duplicate/template cluster assignments; agency response text and final-rule linkage | Docket schema and volume moments exist, but body-level duplicate clusters and agency-response uptake links are not yet committed. |
| venue-shifting-detection-effect | partial_identifier_support_not_linkage_ready | candidate_only_blocked (required=5; ready=0; candidateOnly=5; missing=0; schemaIssues=0) | LDA rows=121; FEC rows=1268; docket rows=200; procurement action rows=28104; intermediary rows=1353; revolving-door proxy rows=803; candidate cross-source actor keys=659; cross-venue keys=140; source systems=8; venues=6 | canonical actor identifier table; alias-resolution rules and manual audit sample; issue-code crosswalk across venues; false-positive and false-negative review log; linked actor-issue-venue-time output table | Multiple public surfaces are present, but the committed snapshot lacks an audited entity-resolution spine. |

## Boundaries and Next Actions

| Target | Bounded or proxy support | Claim boundary | Next action |
| --- | --- | --- | --- |
| substitution-elasticity | Direct dark money: direct-proxy-bounded (usable; darkMoneyDirectRoutingRows=80); Intermediaries: proxy-bounded (usable; intermediaryRows=1353); Revolving door: proxy-thin (usable; revolvingDoorRows=803); first-wave linkage candidates: candidate-only (659 cross-source keys; 140 cross-venue keys; maxSources=3; maxVenues=3) | May guide a source-anchored substitution design; does not validate hidden-channel magnitudes or causal substitution effects. | Choose one named reform shock, use the candidate-only entity-resolution seed files to prioritize manual actor review, build the actor-issue-time linkage file, and record exposed plus comparison actors before inspecting outcome movement. |
| procurement-modification-causal-capture | sam-contract-awards-action-history: implemented-not-active (snapshotRows=0); representative SAM/FPDS action history: blocked | Supports procurement denominator and stress diagnostics only; does not support causal procurement-modification capture claims. | Normalize a SAM/FPDS export through the existing importer, then reconcile modification fields against USAspending before adding protest, exclusion, and firewall overlays. |
| comment-authenticity-and-uptake-effect | Rulemaking comments: source-moment-only (regulatory rows=200; no separate source-panel row) | Supports rulemaking information-distortion design and source moments only; does not estimate comment-authenticity effects. | Select a docket family, archive comment bodies and duplicate clusters, then link comments to response sections and final-rule text before estimating uptake. |
| venue-shifting-detection-effect | Direct dark money: direct-proxy-bounded (usable; darkMoneyDirectRoutingRows=80); Intermediaries: proxy-bounded (usable; intermediaryRows=1353); Revolving door: proxy-thin (usable; revolvingDoorRows=803); first-wave linkage candidates: candidate-only (659 cross-source keys; 140 cross-venue keys; maxSources=3; maxVenues=3) | Can support a detection-measurement workplan; cannot prove venue shifting changed outcomes. | Start from the candidate-only entity-resolution seed files, adjudicate aliases linking LDA clients, FEC spenders, docket submitters, vendors, intermediaries, and access proxies, then audit false matches before promoting the panel. |
