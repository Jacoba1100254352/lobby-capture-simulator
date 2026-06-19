# Lobby Capture Simulator

Standalone Java simulation focused on lobbying, money in politics, regulatory capture, and anti-capture reforms.

This repository implements the Lobby Capture Simulator described in `PROJECT_PLAN.md`. It treats lobby organizations as strategic budget allocators across influence channels, then resolves outcomes in legislative, rulemaking, election, procurement, litigation, enforcement, and public-information arenas.

## Run

```sh
make test
make run ARGS="--list"
make run ARGS="--scenario reform-threat-mobilization --runs 10 --contests 30 --seed 7"
make campaign
make mechanism-comparison
make sensitivity
make ablation
make interactions
make portfolio
make source-moments
make validate
make calibration-queue
make snapshot-2024-env
make tables
make figures
make scrub-copy-suffix-artifacts
make paper
make paper-word-count
make wiley-template
make wiley-tex-deps
make paper-wiley
make submission-package
make paper-artifacts
make paper-artifacts-check
make wiley-submission-form-readiness-audit
make github-ci-status-audit
make external-finalization-checklist
```

`make campaign` writes:

- `reports/lobby-capture-campaign.csv`
- `reports/lobby-capture-campaign.md`

`make mechanism-comparison` writes:

- `reports/lobby-capture-mechanism-comparison.csv`
- `reports/lobby-capture-mechanism-comparison.md`

`make sensitivity` writes:

- `reports/lobby-capture-sensitivity.csv`
- `reports/lobby-capture-sensitivity.md`

`make ablation` writes:

- `reports/lobby-capture-ablation.csv`
- `reports/lobby-capture-ablation.md`

`make interactions` writes:

- `reports/lobby-capture-interactions.csv`
- `reports/lobby-capture-interactions.md`

`make portfolio` writes:

- `reports/lobby-capture-portfolio.csv`
- `reports/lobby-capture-portfolio.md`

Each report run also writes a `*.manifest.json` sidecar with seed, runs, contests, command, runtime provenance, source Git state, and calibration checksum. The committed review artifacts use a stable runtime-provenance label so Java 21 CI and local Java runtimes do not rewrite otherwise identical report snapshots. The Git-state field excludes tracked generated reports, paper tables, paper figures, and the pinned 2024-env snapshot outputs so rerunning the report suite does not falsely mark later manifests dirty because earlier generated artifacts changed. `make validate` compares committed report snapshots against benchmark plausibility ranges and writes:

- `reports/validation-summary.csv`
- `reports/validation-summary.md`

Validation now also reads `data/calibration/parameter-map.csv`, which classifies targets as observed, inferred, proxy, sectoral, or judgmental. The parameter map is the bridge from the Deep Research reports to simulator metrics.

`make source-moments` writes direct diagnostics from normalized source tables:

- `reports/source-moments.csv`
- `reports/source-moments.md`

`make calibration-queue` classifies validation misses and partial overlaps into model-tuning, metric-split, source-moment, scenario-coverage, scale-alignment, or benchmark-review work.

The fetch scripts seed normalized local calibration data from tracked fixtures:

```sh
./scripts/fetch-lda.sh
./scripts/fetch-fec.sh
./scripts/fetch-regulatory.sh
./scripts/fetch-usaspending.sh
./scripts/fetch-revolving-door.sh
./scripts/fetch-public-financing.sh
./scripts/fetch-intermediaries.sh
```

## Data Credentials

`.env.example` lists every configured source variable. Copy it to `.env` and fill in private values there; `.env` is ignored by git and the fetch scripts load it automatically.

Credential and source-access links:

- LDA API key: <https://lda.gov/api/register/>
- FEC/OpenFEC API key: <https://api.data.gov/signup/>
- Regulations.gov API key: <https://api.data.gov/signup/>
- Regulations.gov API docs: <https://open.gsa.gov/api/regulationsgov/>
- USAspending API docs: <https://api.usaspending.gov/docs/endpoints> (no key currently required)
- SAM.gov public APIs: <https://open.gsa.gov/api/>
- OpenSecrets API/account access: <https://www.opensecrets.org/api/admin/index.php>
- ProPublica Nonprofit Explorer API: <https://projects.propublica.org/nonprofits/api>
- LegiStorm API/account access: <https://www.legistorm.com/api.html>

Optional live normalization uses the same output schemas. You can pass an explicit local CSV/URL, or let the scripts query their upstream source-native APIs:

```sh
LDA_LIVE_CSV=/path/to/lda.csv ./scripts/fetch-lda.sh --live
FEC_LIVE_URL=https://example.org/fec.csv ./scripts/fetch-fec.sh --live
REGULATORY_LIVE_CSV=/path/to/dockets.csv ./scripts/fetch-regulatory.sh --live
USASPENDING_LIVE_CSV=/path/to/awards.csv ./scripts/fetch-usaspending.sh --live
REVOLVING_DOOR_LIVE_CSV=/path/to/revolving-door.csv ./scripts/fetch-revolving-door.sh --live
PUBLIC_FINANCING_LIVE_CSV=/path/to/public-financing.csv ./scripts/fetch-public-financing.sh --live
INTERMEDIARY_LIVE_CSV=/path/to/nonprofit-association-panel.csv ./scripts/fetch-intermediaries.sh --live
SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/sam-contract-awards-export.csv ./scripts/run-2024-env-live-snapshot.sh

LDA_API_KEY=... ./scripts/fetch-lda.sh --live
FEC_API_KEY=... ./scripts/fetch-fec.sh --live
FEC_API_KEY=... FEC_ONLY_SCHEDULE_E=1 ./scripts/fetch-fec.sh --live
FEC_API_KEY=... FEC_ONLY_SCHEDULE_E=1 FEC_INCLUDE_ELECTIONEERING=1 FEC_INCLUDE_COMMUNICATION_COSTS=1 ./scripts/fetch-fec.sh --live
REGULATIONS_API_KEY=... ./scripts/fetch-regulatory.sh --live
REGULATORY_SOURCE=federal-register ./scripts/fetch-regulatory.sh --live
./scripts/fetch-usaspending.sh --live
SAM_API_KEY=... python3 scripts/fetch-source-data.py sam-contract-awards --output data/raw/sam-contract-awards.csv
REVOLVING_DOOR_SOURCE_NATIVE=1 python3 scripts/fetch-source-data.py revolving-door --output data/raw/revolving-door.csv
```

The pinned 2024 EPA/ENV live runner is:

```sh
scripts/run-2024-env-live-snapshot.sh
```

It preserves raw public API payloads under ignored `data/raw/source-payloads/2024-env/`, writes normalized rows into `data/raw/`, runs the snapshot freezer, and emits source moments. If no personal API keys are configured it uses official public/demo access where possible and records rate-limit gaps in `data/snapshots/2024-env/live-run-status.csv`. Set `SAM_CONTRACT_AWARDS_LIVE_CSV` or `SAM_CONTRACT_AWARDS_LIVE_URL` to normalize a downloaded SAM.gov Contract Awards CSV/JSON/ZIP export as the primary procurement action panel. For SAM.gov emailed async-extract links, prefer `make sam-contract-awards-record-export-link < sam-email.txt` or `python3 scripts/record-sam-export-link.py --url 'https://api.sam.gov/contract-awards/v1/download?...'`; the helper writes the URL and expiration metadata into `.env`, keeps the private key in `SAM_API_KEY`, clears stale `SAM_CONTRACT_AWARDS_LIVE_CSV` overrides, and prints only redacted diagnostics. If no export is configured, set `SAM_CONTRACT_AWARDS_SOURCE_NATIVE=1` with `SAM_API_KEY` to try the SAM.gov Contract Awards API; the runner records SAM availability and falls back to USAspending action rows if that opt-in request fails.

Before promoting a downloaded SAM export, run `SAM_CONTRACT_AWARDS_LIVE_CSV=/path/to/export.csv make sam-contract-awards-export-audit` or `SAM_CONTRACT_AWARDS_LIVE_URL='https://api.sam.gov/contract-awards/v1/download?api_key=REPLACE_WITH_API_KEY&token=...' make sam-contract-awards-export-audit`. The audit writes ignored operational reports under `reports/sam-contract-awards-export-audit.*` and checks row count, agency breadth, date span, PIID coverage, UEI coverage, competition fields, modification denominators, and raw export coverage for action-date and amount fields. If SAM.gov returns a quota or token-download failure, the audit still writes a redacted report with the HTTP status and any `nextAccessTime`, but does not promote rows. Its markdown report also writes a next-export specification with the minimum representative-agency, field-family, and action-history requirements to fix blocked exports, including the common case where a solicitation-date extract lacks action dates and obligation amounts. A candidate audit result is still only a pre-promotion screen; the paper snapshot must then be regenerated and pass `make paper-artifacts-check`.

For an emailed SAM.gov async-export link, run `make sam-contract-awards-record-export-link < sam-email.txt` immediately after the email arrives, or pass the URL directly to `python3 scripts/record-sam-export-link.py --url ... --generated-at YYYY-MM-DDTHH:MM:SSZ`. If `sam-email.txt` includes a standard email `Date:` header, the helper uses that timestamp as the token generation time; otherwise use an explicit `--generated-at` value. Body-only pasted emails with no `Date:` header now fail closed unless you use `make sam-contract-awards-record-fresh-link < sam-email-body.txt` or pass `--assume-fresh`; that override should be used only when the email was just generated. If several SAM.gov emails are pasted together, `--url-selection auto` chooses the latest dated URL, or the last URL when dates are unavailable. Timestamped links that have already expired are rejected by default before `.env` is changed; use `--allow-expired` only for fixtures or diagnostics. Treat `timeSource=recorded_at_fallback` as usable only for an intentional `--assume-fresh` body-only capture; overnight or otherwise delayed messages should be discarded and replaced with a fresh export email. The helper stores `SAM_CONTRACT_AWARDS_LIVE_URL` with `api_key=REPLACE_WITH_API_KEY`, records generation, expiration, validity-window, recorded-at, and timestamp-source metadata, and clears `SAM_CONTRACT_AWARDS_LIVE_CSV` unless `--keep-live-csv` is supplied. `make sam-contract-awards-export-audit` substitutes the key at runtime, redacts both key and token from diagnostics, and treats an explicitly expired emailed link as a manual-refresh condition rather than a promotable source. If SAM.gov returns a quota reset after the emailed token expires, the export audit records that retry window and `make external-finalization-checklist` keeps the SAM input manual rather than treating the still-fresh token as promotable. The checklist summarizes whether a SAM export URL/CSV, GitHub release asset audit, GitHub CI audit, Zenodo token/draft/upload state, DOI record, human read-through, and live journal-guideline refresh are ready, manual, or blocked. Its reports are ignored because they can reflect private `.env` and live release state.

For the remaining procurement-source refresh, prefer the guarded wrapper:

```sh
make sam-procurement-refresh
```

It uses a configured `SAM_CONTRACT_AWARDS_LIVE_CSV`/`SAM_CONTRACT_AWARDS_LIVE_URL` as a manual export path when present. Otherwise it runs a mode-matched preflight first: `make sam-contract-awards-preflight-extract` before keyed asynchronous extract mode, or `make sam-contract-awards-preflight-offset` before synchronous offset mode. A green synchronous preflight does not clear extract-mode quota by itself. The wrapper stops with a temporary-failure exit when SAM.gov reports a quota reset time, and only then runs the selected keyed live snapshot plus `make paper-artifacts-check`. Use `scripts/refresh-sam-procurement-panel.sh --dry-run` to inspect the selected mode without spending quota.

The remaining procurement overlay work is tracked by:

```sh
make first-wave-procurement-source-acquisition
```

That report is an acquisition plan, not evidence. It maps the first-wave procurement source products to official public surfaces: SAM.gov Contract Awards for action history and offer-count/competition enrichment, GAO bid protest decisions and Legal Products feed for protest overlays, SAM.gov Exclusions API or public exclusion extracts for exclusion overlays, and agency procurement-integrity documents for firewall controls. Populate the named files under `data/calibration/first-wave/`, then rerun `make first-wave-source-products`, `make first-wave-source-readiness`, and `make paper-artifacts-check` before treating any procurement overlay as source-supported.

For the GAO protest overlay, `make gao-protest-feed-preflight` uses the no-key GAO Legal Products XML feed to write ignored operational reports under `reports/gao-protest-feed-preflight.*`. Those rows are a discovery worklist only: they remain candidate-only until a human review links protest IDs to agency, vendor, PIID/UEI, outcome, issue, and source-page fields in `data/calibration/first-wave/gao-protest-overlay.csv`, followed by the first-wave source-product and paper artifact gates.

`docs/source-data-roadmap.md` records the next source panels and matching identifiers: LDA registrant/client IDs, FEC committee/candidate IDs, IRS EINs, SAM UEIs, PIIDs, docket/document/comment IDs, and official/person records. The project keeps direct observed source rows separate from proxy overlays and synthetic design metrics.

`make snapshot-2024-env` freezes the current normalized source rows under `data/snapshots/2024-env/` and writes a manifest for the first closed-window paper snapshot: 2024 LDA `ENV`, EPA Regulations.gov/Federal Register activity, 2024 OpenFEC national party committee rows, Schedule E independent-expenditure rows, optional electioneering and communication-cost rows, configured public-financing bridge rows, EPA fiscal-year 2024 USAspending awards, the multi-agency procurement concentration bridge, a stratified 12-agency quarterly procurement transaction/action panel for concentration and modification-incidence diagnostics, an LDA-derived covered-position revolving-door panel, and the configured nonprofit/527/association intermediary panel. Live paper snapshots should run the source-native fetchers with those fixed filters before freezing.

`make tables` regenerates LaTeX table files under `paper/tables/` from the committed report CSV snapshots. `make figures` regenerates paper interaction figures under `paper/figures/`. `make paper` runs both generators before building the local PDF. Table selection lives in `paper/tables.yml`, so paper row/column/caption edits do not require changing the generator.

## Paper and Submission Target

The primary paper target is now **Regulation & Governance**. The default build, `make paper`, produces a compile-stable local manuscript from `paper/strategic-channel-substitution-regulatory-capture.tex`. `make paper-word-count` estimates the manuscript against the reported 8,000-10,000-word preferred Regulation & Governance range, including generated references when `paper/strategic-channel-substitution-regulatory-capture.bbl` exists.

The Wiley-template path is available but intentionally separate from the default build:

- `make wiley-template` downloads Wiley's official `WileyDesign.zip` into ignored `paper/.wiley-template/`.
- `make wiley-tex-deps` installs the extra Wiley-template LaTeX packages into the user TeX tree through `tlmgr --usermode`.
- `paper/regulation-governance-wiley.tex` is the Regulation & Governance/Wiley wrapper using Wiley's `USG` class.
- `make paper-wiley` builds the Wiley wrapper after the official bundle and TeX dependencies are available. It writes ignored scratch files under `paper/.wiley-build/` to work around a BibTeX failure in the current Wiley archive's primary Chicago style file while still using the downloaded Wiley class and template assets.
- `make submission-package` builds the Wiley wrapper and writes `dist/lobby-capture-wiley-submission.zip` with the root LaTeX file, compiled PDF, patched peer-review class copy, bibliography, generated tables, PDF graphics, SVG figure sources, LaTeX figure wrappers, supporting-information files, a package-member checksum manifest, and the full generated CSV/Markdown/manifest report bundle. The package ZIP is written with sorted entries and fixed timestamps so archive contents are reproducible across clean builds.
- `make scrub-copy-suffix-artifacts` removes local duplicate-copy artifacts such as `report 2.md`, `paper 2.aux`, or `bundle 2.zip` from `paper/`, `reports/`, and `dist/`. The paper, package, clean, and artifact-check paths run it automatically so local file-sync duplicates cannot enter the Wiley package or block the final checker.
- `make reviewer-risk-register` writes `reports/reviewer-risk-register.{csv,md}` from the readiness, source-dependency, causal-target, source-capability, procurement, policy-language, and final-read-through audits. It is a reviewer-facing construct-validity map: likely concern, current response, evidence boundary, and next action. The report is included directly in the Wiley supporting information, in the report-data bundle, and in the DOI handoff package.
- `make archive-handoff-audit` runs after the Wiley submission archive is built and writes `reports/archive-handoff-manifest.{csv,json,md}` with the DOI-deposit asset set and stable source-metadata checksums. It also writes ignored `dist/release-asset-checksums.{csv,json,md}` with local PDF/ZIP SHA-256 checksums for release upload verification. The tracked manifest is intentionally kept outside the Wiley ZIP and avoids environment-specific binary hashes.
- `make github-release-upload-paths` prints the exact release asset paths expected by the GitHub release audit. Use this list when creating or replacing a release instead of reading every row from `dist/release-asset-checksums.csv`, because some checksum rows are source-archive metadata and are not standalone release assets.
- `make github-release-asset-audit` is a post-release, networked check that uses `gh release view` to compare uploaded GitHub release assets against the local release-machine checksum manifests. It writes ignored `reports/github-release-asset-audit.{csv,md}` and is intentionally excluded from `make paper-artifacts-check` so the standard reviewer build remains offline-reproducible.
- `make github-ci-status-audit` is a post-release, networked check that uses `gh run list` to verify the current main commit and the current release tag both have completed, successful GitHub Actions CI runs. It writes ignored `reports/github-ci-status-audit.{csv,md}` and is folded into `make external-finalization-checklist`.
- `make release-postflight` is the one-command post-release handoff. Run it after pushing the release tag and uploading release assets; it runs the GitHub release-asset audit, the GitHub CI-status audit, and then regenerates the ignored external-finalization checklist so the local DOI/journal/SAM handoff state cannot remain on an older release tag.
- `make zenodo-deposit-preflight` writes ignored `dist/zenodo-deposit-metadata.json` plus tracked `reports/zenodo-deposit-preflight.{csv,md}`. It validates the Zenodo metadata, DOI package, claim boundary, and remaining manual gates without using the network or asserting that a DOI exists. With a Zenodo token configured as `ZENODO_ACCESS_TOKEN`, `ZENODO_API_TOKEN`, `ZENODO_TOKEN`, or the target-specific `ZENODO_SANDBOX_TOKEN`/`ZENODO_PRODUCTION_TOKEN`, `make zenodo-deposit-draft` creates or updates an unpublished Zenodo draft, and `make zenodo-deposit-upload` uploads `dist/lobby-capture-doi-deposit-package.zip` to that unpublished draft. These targets never publish a Zenodo record.
- `make doi-deposit-package` builds ignored `dist/lobby-capture-doi-deposit-package.zip` plus `dist/doi-deposit-package-manifest.{json,md}` and `dist/doi-deposit-package-checksum.{csv,json,md}` as a single archive handoff package containing the primary release assets, checksum files, citation metadata, journal-readiness reports, and final human read-through checklist. The DOI readiness report remains outside that ZIP so it can verify the package after construction.
- `make external-finalization-checklist` writes ignored `reports/external-finalization-checklist.{csv,md}` from the latest local readiness reports and live/private environment state. It sources `.env`, folds in the post-release GitHub asset and CI audits if present, records Zenodo draft/upload state if present, checks whether a DOI has been recorded in repository metadata, and reports SAM.gov export-input readiness without leaking keys or emailed export tokens. The checklist reports DOI/journal finalization separately from source-refresh promotion, so a blocked SAM export blocks only promotion of that source into a refreshed snapshot. Run `make paper-artifacts-check` separately before creating or replacing release assets.
- `make wiley-submission-form-readiness-audit` runs after the Wiley submission archive is built and writes `reports/wiley-submission-form-readiness.{csv,md}`. It checks generic Wiley upload mechanics such as file size, file-name length, root LaTeX/PDF presence, support files, unsupported executable/script formats, and required manuscript statements, while leaving journal-specific author-guidelines refresh as a manual final-submission step.
- `make reggov-guidelines-readiness-audit` runs after the Wiley upload-form audit and writes `reports/reggov-guidelines-readiness.{csv,md}`. It checks locally verifiable Regulation & Governance/Wiley requirements: journal target metadata, original-article wrapper, 8,000-10,000-word preferred range, abstract and keywords, title-page metadata, data/code availability, AI/funding/conflict disclosures, figures, tables, supporting information, and LaTeX package contents. It still leaves the live Regulation & Governance author page refresh as a manual final-submission step.
- `make paper-artifacts` is the full paper refresh target. It reruns the committed report sweeps, mechanism comparison, portfolio screen, source moments, validation, causal-calibration and first-wave source-product gates, calibration queue, tables, figures, local PDF, Wiley PDF, word count, and submission zip.
- `make paper-artifacts-check` runs the same refresh and then verifies the local PDF, Wiley PDF, supplement PDF, layout audit, visual-review checklist, and submission zip are present, fresh relative to their inputs, free of generic Wiley-template placeholder text, and internally consistent. CI uses this target so stale paper inputs cannot pass without rebuilding the PDFs and submission package.

Makefile report targets set deterministic `LOBBY_CAPTURE_REPORT_TIMESTAMP` and `LOBBY_CAPTURE_REPORT_GIT_COMMIT` values so committed CSV, Markdown, and manifest artifacts can be regenerated without timestamp/provenance-only diffs. Direct `java -cp out/classes lobbycapture.Main ...` runs still use the live clock and current Git commit unless those variables or `SOURCE_DATE_EPOCH` are set.

The Wiley build patches only the generated `.wiley-build/USG.cls` copy to remove generic template sample journal art, the sample Open Access badge, and placeholder publication metadata. The downloaded Wiley template remains unmodified under ignored `paper/.wiley-template/`.

Submission strategy details live in `docs/submission-strategy.md`.

## Citation and Archive Metadata

Use the versioned GitHub release named in the paper's Data and Code Availability statement when citing the review bundle. `CITATION.cff` provides machine-readable software and preferred-paper citation metadata, and `.zenodo.json` provides release metadata for DOI archiving if the GitHub repository is connected to Zenodo. `reports/archive-handoff-manifest.*` records the DOI-deposit asset set and stable metadata checksums, `reports/reviewer-risk-register.*` records likely reviewer objections and the current evidence boundaries, `reports/zenodo-deposit-preflight.*` records the prepared Zenodo payload and unpublished-draft workflow, `reports/wiley-submission-form-readiness.*` records post-package upload-form readiness, `reports/reggov-guidelines-readiness.*` records locally verifiable journal-guideline readiness, while ignored `dist/release-asset-checksums.*` records local PDF/ZIP SHA-256 checksums for the release machine. After uploading release assets and waiting for GitHub Actions, run `make release-postflight`; it verifies uploaded asset digests and sizes, records whether CI passed for both main and the release tag, and refreshes the local external-finalization checklist for the same release. `dist/lobby-capture-doi-deposit-package.zip` is a convenience package for DOI deposit workflows that need a single upload artifact; its ignored manifest records member-level checksums and `dist/doi-deposit-package-checksum.*` records the package ZIP checksum. The Wiley submission package includes copies of both metadata files under `supporting-information/`, a checksum manifest under `supporting-information/submission-package-manifest.*`, plus the full generated report bundle under `supporting-information/report-data/`. `make paper-artifacts-check` fails if those files are missing, stale, byte-different from the working tree where applicable, internally inconsistent with the package manifests, inconsistent with the archive-handoff manifest, or no longer point at the current review-bundle tag.

`reports/submission-readiness.md` separates mechanism-review readiness from final journal-submission signoff. A `ready_for_mechanism_review` posture means the bundle is reproducible and claim-bounded for review as a mechanism-model article; the separate `final-journal-submission` gate records external requirements such as DOI archiving and human scholarly read-through signoff. The manual read-through checklist lives at `reports/final-human-readthrough.md`, and `make final-human-readthrough-audit` turns its fields and checklist items into `reports/final-human-readthrough-audit.{csv,md}`. Pending scholarly items remain `manual_required` for review-bundle circulation, while malformed records or a completed signoff with unchecked items become `blocked`.

`make external-finalization-checklist` is the local handoff command to run while preparing final external steps. It does not replace `make paper-artifacts-check`; instead, it keeps private or live-state tasks out of the deterministic build and tells whether the release asset audit, GitHub CI audit, Zenodo token/draft/upload, DOI metadata record, human read-through, live author-page refresh, and configured SAM.gov export are ready for the next manual action.

`make first-wave-source-product-templates` writes acquisition templates under `docs/source-product-templates/first-wave/`, including CSV headers, the meeting/contact missing-channel design-note template, and a template manifest. These files are scaffolds only: they intentionally live outside `data/calibration/first-wave/` and cannot satisfy the source-product gate. `make first-wave-comment-products` is a networked helper that uses `REGULATIONS_API_KEY` to build a bounded public Regulations.gov comment-body corpus and reproducible duplicate/template cluster product for the configured docket under `data/calibration/first-wave/`; those products support comment-authenticity design but do not provide agency-response uptake or final-rule linkage. `make first-wave-source-products` writes `reports/first-wave-source-products.csv` plus `reports/first-wave-source-products.md`. It converts the first-wave causal protocols into executable source-product schemas under `data/calibration/first-wave/`, including expected paths, template paths, required columns or text terms, acceptable source families, field-level quality checks, validation rules, and claim boundaries. `make first-wave-source-readiness` consumes that schema gate before any first-wave protocol can move from design-ready to estimation-ready.

The source-native fetcher has tiny checked-in JSON fixtures under `data/fixtures/source-native/`, including OpenFEC contribution, electioneering, communication-cost, USAspending award/transaction, and SAM.gov Contract Awards payloads. `make test` verifies those parser paths without hitting the network. Live source requests retry transient `429` and `5xx` responses; tune with `SOURCE_FETCH_RETRIES`, `SOURCE_FETCH_BACKOFF_SECONDS`, `SOURCE_FETCH_TIMEOUT_SECONDS`, and `SOURCE_FETCH_HARD_TIMEOUT_SECONDS`.

## Current Modeling Slice

The MVP answers a narrow question from the project plan:

> When organized interests face a meaningful anti-capture reform threat, do they shift from ordinary policy capture to defensive reform blocking, and which reforms remain effective after that adaptation?

It includes:

- finite disclosed, dark-money, legal, campaign, grassroots, and research budgets;
- explicit client funding and client-to-lobby money flows;
- adaptive channel selection, channel-return memory, per-client/per-domain funding multipliers, regulator attention queues, watchdog monitoring budgets, and reform-decay pressure;
- direct access, agenda access, information distortion, public campaigns, litigation threats, campaign finance, dark money, revolving-door access, and defensive reform spending;
- first-class rulemaking dockets, comment campaigns, authenticity, template saturation, and technical-claim credibility;
- comment-record triage with unique-information share, duplicate compression, review burden, procedural acknowledgment, and substantive uptake;
- split validation-facing source metrics for all-flow traceability, non-proxy direct dark-money routing rows, direct dark-money visibility, Schedule E/electioneering/communication-cost outside-spending pressure, resident voucher participation, candidate public-financing uptake, procurement bridge coverage, intermediary donor disclosure, revolving-door source confidence, narrow reporting-error detection, and campaign sanction incidence;
- evasion profiles with dark-pool, litigation-funding, procurement-consultant, and revolving-door substitution pressure;
- an influence-substitution engine that reports hidden influence, preserved influence capacity, messenger substitution, venue substitution, and net transparency gain after reforms constrain a channel;
- an influence-network diagnostic layer that reports modeled path opacity, donor concentration, intermediary centrality, official-access centrality, procurement exposure, revolving-door bridges, comment-network load, venue-shift load, legibility, cross-venue detection, participation protection, and speech-restriction risk;
- arena-specific capture susceptibility;
- transparency, public financing, democracy vouchers, cooling-off, blind review, public advocates, enforcement, anti-astroturf systems, defensive-spend caps, and dark-money disclosure;
- raw and composite scenario metrics plus sensitivity, ablation, adaptation-speed, and reform-decay metrics.
- validation summaries, substitution-warning audits, mechanism comparisons, portfolio screens, and two-way reform interaction sweeps.
- wide generated paper tables, vector/PDF figures, and a Wiley submission-package target.

The formulas are stylized and comparative. Empirical files under `data/calibration/` and normalized fixtures under `data/fixtures/` are benchmark scaffolds, not causal estimates.
