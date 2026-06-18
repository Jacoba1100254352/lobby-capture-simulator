JAVAC ?= javac
JAVA ?= java
PDFLATEX ?= $(or $(shell command -v pdflatex 2>/dev/null),$(firstword $(wildcard /usr/local/texlive/2026basic/bin/universal-darwin/pdflatex /usr/local/texlive/2025basic/bin/universal-darwin/pdflatex /Library/TeX/texbin/pdflatex /opt/homebrew/bin/pdflatex /usr/local/bin/pdflatex)),pdflatex)
BIBTEX ?= $(or $(shell command -v bibtex 2>/dev/null),$(firstword $(wildcard /usr/local/texlive/2026basic/bin/universal-darwin/bibtex /usr/local/texlive/2025basic/bin/universal-darwin/bibtex /Library/TeX/texbin/bibtex /opt/homebrew/bin/bibtex /usr/local/bin/bibtex)),bibtex)
REPORT_GENERATED_AT ?= 2026-05-05T00:00:00Z
REPORT_GIT_COMMIT ?= tracked-artifact-build
REPORT_GIT_DIRTY ?= false
REPORT_JAVA_VERSION ?= tracked-artifact-build
REPORT_ENV := LOBBY_CAPTURE_REPORT_TIMESTAMP=$(REPORT_GENERATED_AT) LOBBY_CAPTURE_REPORT_GIT_COMMIT=$(REPORT_GIT_COMMIT) LOBBY_CAPTURE_REPORT_WORKING_TREE_DIRTY=$(REPORT_GIT_DIRTY) LOBBY_CAPTURE_REPORT_JAVA_VERSION=$(REPORT_JAVA_VERSION)

MAIN_SOURCES := $(shell find src/main/java -name "*.java" | sort)
TEST_SOURCES := $(shell find src/test/java -name "*.java" | sort)
MAIN_CLASS := lobbycapture.Main
TEST_CLASSES := lobbycapture.SimulatorTests
PAPER_BASENAME := strategic-channel-substitution-regulatory-capture

.PHONY: compile script-checks test run campaign mechanism-comparison sensitivity ablation interactions portfolio source-moments source-panel-inventory source-capability-audit dark-money-bridge-audit intermediary-bridge-audit revolving-door-bridge-audit procurement-denominator-audit procurement-modification-composition-audit procurement-benchmark-crosswalk procurement-refresh-readiness sam-contract-awards-preflight sam-contract-awards-export-audit sam-contract-awards-record-export-link usaspending-transaction-download-strata sam-procurement-refresh claim-boundary-audit claim-source-dependency-audit causal-calibration-targets first-wave-causal-protocols first-wave-source-product-templates first-wave-entity-resolution-seeds first-wave-comment-products first-wave-comment-linkage-seeds first-wave-source-products first-wave-linkage-candidates first-wave-source-readiness claim-posture-audit validation-scope-coverage calibration-readiness-audit policy-claim-language-audit final-human-readthrough-audit submission-readiness-audit reviewer-risk-register archive-handoff-audit github-release-asset-audit github-ci-status-audit zenodo-deposit-preflight zenodo-deposit-draft zenodo-deposit-upload record-doi-archive doi-deposit-readiness-audit external-finalization-checklist wiley-submission-form-readiness-audit reggov-guidelines-readiness-audit doi-deposit-package latex-log-audit calibration-queue validate snapshot-2024-env tables figures scrub-copy-suffix-artifacts paper paper-build paper-supplement-build paper-supplement paper-word-count wiley-template wiley-tex-deps paper-wiley paper-wiley-build submission-package submission-package-build submission-package-check paper-layout-audit visual-review-checklist paper-artifacts paper-artifacts-check clean

compile:
	@mkdir -p out/classes
	$(JAVAC) -d out/classes $(MAIN_SOURCES)

script-checks:
	python3 -m py_compile scripts/*.py
	@for script in scripts/*.sh; do \
		bash -n $$script || exit $$?; \
	done

test: script-checks compile
	@mkdir -p out/test-classes
	$(JAVAC) -cp out/classes -d out/test-classes $(TEST_SOURCES)
	@for test_class in $(TEST_CLASSES); do \
		$(JAVA) -cp out/classes:out/test-classes $$test_class || exit $$?; \
	done
	./scripts/test-normalizers.sh

run: compile
	$(JAVA) -cp out/classes $(MAIN_CLASS) $(ARGS)

campaign: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --campaign --runs 40 --contests 80 --seed 42

mechanism-comparison: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --mechanism-comparison --runs 40 --contests 80 --seed 542

sensitivity: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --sensitivity --runs 30 --contests 70 --seed 142

ablation: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --ablation --runs 40 --contests 80 --seed 242

interactions: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --interactions --runs 25 --contests 60 --seed 342

portfolio: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --portfolio --runs 35 --contests 70 --seed 442

source-moments:
	python3 scripts/extract-source-moments.py

source-panel-inventory: source-moments
	python3 scripts/audit-source-panels.py

source-capability-audit: source-panel-inventory
	python3 scripts/audit-source-capabilities.py

dark-money-bridge-audit: source-moments
	python3 scripts/audit-dark-money-bridge.py

intermediary-bridge-audit: source-moments
	python3 scripts/audit-intermediary-bridge.py

revolving-door-bridge-audit: source-moments
	python3 scripts/audit-revolving-door-bridge.py

procurement-denominator-audit: source-moments
	python3 scripts/audit-procurement-denominator.py

procurement-modification-composition-audit: source-moments
	python3 scripts/audit-procurement-modification-composition.py

procurement-benchmark-crosswalk: source-moments
	python3 scripts/audit-procurement-benchmark-crosswalk.py

procurement-refresh-readiness: source-capability-audit procurement-denominator-audit calibration-queue
	$(REPORT_ENV) python3 scripts/write-procurement-refresh-readiness.py

sam-contract-awards-preflight:
	python3 scripts/probe-sam-contract-awards.py

sam-contract-awards-export-audit:
	@. ./scripts/load-env.sh; python3 scripts/audit-sam-contract-awards-export.py

sam-contract-awards-record-export-link:
	python3 scripts/record-sam-export-link.py --input -

usaspending-transaction-download-strata:
	@. ./scripts/load-env.sh; python3 scripts/audit-usaspending-transaction-download-strata.py

sam-procurement-refresh:
	./scripts/refresh-sam-procurement-panel.sh

calibration-queue: validate
	python3 scripts/classify-validation-misses.py

validate: source-moments source-panel-inventory
	python3 scripts/validate-reports.py

validation-scope-coverage: validate
	python3 scripts/audit-validation-scope-coverage.py

claim-boundary-audit: validate
	python3 scripts/audit-claim-boundaries.py

claim-source-dependency-audit: claim-boundary-audit
	python3 scripts/audit-claim-dependencies.py

causal-calibration-targets: claim-source-dependency-audit
	python3 scripts/audit-causal-calibration-targets.py

first-wave-causal-protocols: causal-calibration-targets
	python3 scripts/write-first-wave-causal-protocols.py

first-wave-source-product-templates:
	python3 scripts/write-first-wave-source-product-templates.py

first-wave-linkage-candidates:
	python3 scripts/build-first-wave-linkage-candidates.py

first-wave-entity-resolution-seeds: first-wave-linkage-candidates
	python3 scripts/build-first-wave-entity-resolution-seeds.py

first-wave-comment-products:
	@. ./scripts/load-env.sh; python3 scripts/build-first-wave-comment-products.py

first-wave-comment-linkage-seeds:
	python3 scripts/build-first-wave-comment-linkage-seeds.py

first-wave-source-products: first-wave-causal-protocols first-wave-source-product-templates first-wave-entity-resolution-seeds first-wave-comment-linkage-seeds
	python3 scripts/audit-first-wave-source-products.py

first-wave-source-readiness: first-wave-causal-protocols first-wave-source-products first-wave-linkage-candidates source-capability-audit procurement-refresh-readiness
	python3 scripts/audit-first-wave-source-readiness.py

snapshot-2024-env:
	python3 scripts/create-2024-env-snapshot.py

tables: claim-source-dependency-audit first-wave-causal-protocols
	python3 scripts/generate-paper-tables.py

figures: claim-boundary-audit
	python3 scripts/generate-interaction-figures.py

scrub-copy-suffix-artifacts:
	@for scan_root in paper reports dist; do \
		[ -d $$scan_root ] || continue; \
		find $$scan_root -type f \( \
			-name '* [0-9]*.aux' -o \
			-name '* [0-9]*.bbl' -o \
			-name '* [0-9]*.blg' -o \
			-name '* [0-9]*.bst' -o \
			-name '* [0-9]*.cff' -o \
			-name '* [0-9]*.cls' -o \
			-name '* [0-9]*.csv' -o \
			-name '* [0-9]*.eps' -o \
			-name '* [0-9]*.json' -o \
			-name '* [0-9]*.log' -o \
			-name '* [0-9]*.md' -o \
			-name '* [0-9]*.out' -o \
			-name '* [0-9]*.pag' -o \
			-name '* [0-9]*.pdf' -o \
			-name '* [0-9]*.sty' -o \
			-name '* [0-9]*.svg' -o \
			-name '* [0-9]*.tex' -o \
			-name '* [0-9]*.txt' -o \
			-name '* [0-9]*.zip' \
		\) -print -delete; \
	done

paper-build: scrub-copy-suffix-artifacts
	find paper -maxdepth 1 -type f \( \
		-name '$(PAPER_BASENAME) [0-9]*.aux' -o \
		-name '$(PAPER_BASENAME) [0-9]*.bbl' -o \
		-name '$(PAPER_BASENAME) [0-9]*.blg' -o \
		-name '$(PAPER_BASENAME) [0-9]*.log' -o \
		-name '$(PAPER_BASENAME) [0-9]*.out' -o \
		-name '$(PAPER_BASENAME) [0-9]*.pag' -o \
		-name '$(PAPER_BASENAME) [0-9]*.pdf' -o \
		-name '$(PAPER_BASENAME) [0-9]*.tex' \
	\) -exec rm -f {} +
	rm -f paper/$(PAPER_BASENAME).aux paper/$(PAPER_BASENAME).bbl paper/$(PAPER_BASENAME).blg
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(BIBTEX) $(PAPER_BASENAME)
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex

paper-supplement-build: scrub-copy-suffix-artifacts
	find paper -maxdepth 1 -type f \( \
		-name 'supplement [0-9]*.aux' -o \
		-name 'supplement [0-9]*.bbl' -o \
		-name 'supplement [0-9]*.blg' -o \
		-name 'supplement [0-9]*.log' -o \
		-name 'supplement [0-9]*.out' -o \
		-name 'supplement [0-9]*.pag' -o \
		-name 'supplement [0-9]*.pdf' -o \
		-name 'supplement [0-9]*.tex' \
	\) -exec rm -f {} +
	rm -f paper/supplement.aux paper/supplement.bbl paper/supplement.blg
	cd paper && $(PDFLATEX) -interaction=nonstopmode supplement.tex
	cd paper && $(PDFLATEX) -interaction=nonstopmode supplement.tex

paper-supplement: tables figures paper-supplement-build

paper: tables figures paper-build paper-supplement-build

paper-word-count:
	python3 scripts/check-paper-word-count.py

wiley-template:
	./scripts/fetch-wiley-template.sh

wiley-tex-deps:
	./scripts/install-wiley-tex-deps.sh

paper-wiley-build: scrub-copy-suffix-artifacts wiley-template
	./scripts/build-wiley-paper.sh

paper-wiley: tables figures paper-wiley-build

submission-package-build: scrub-copy-suffix-artifacts reviewer-risk-register
	./scripts/build-submission-package.sh

submission-package-check: submission-package-build
	./scripts/check-submission-package.sh

submission-package: paper-wiley paper-supplement paper-word-count visual-review-checklist latex-log-audit policy-claim-language-audit submission-readiness-audit reviewer-risk-register first-wave-causal-protocols first-wave-source-product-templates first-wave-linkage-candidates first-wave-entity-resolution-seeds first-wave-source-products first-wave-source-readiness submission-package-build submission-package-check archive-handoff-audit

paper-layout-audit: paper-build paper-wiley-build paper-supplement-build
	python3 scripts/audit-paper-layout.py

visual-review-checklist: paper-layout-audit
	python3 scripts/write-visual-review-checklist.py

latex-log-audit: paper-build paper-wiley-build paper-supplement-build
	python3 scripts/audit-latex-logs.py

claim-posture-audit: claim-boundary-audit claim-source-dependency-audit causal-calibration-targets first-wave-causal-protocols calibration-queue visual-review-checklist
	python3 scripts/audit-claim-posture.py

calibration-readiness-audit: claim-posture-audit validation-scope-coverage
	python3 scripts/audit-calibration-readiness.py

policy-claim-language-audit: calibration-readiness-audit
	python3 scripts/audit-policy-claim-language.py

final-human-readthrough-audit:
	python3 scripts/audit-final-human-readthrough.py

submission-readiness-audit: policy-claim-language-audit final-human-readthrough-audit
	python3 scripts/audit-submission-readiness.py

reviewer-risk-register: submission-readiness-audit calibration-readiness-audit claim-source-dependency-audit causal-calibration-targets source-capability-audit source-panel-inventory procurement-refresh-readiness final-human-readthrough-audit
	python3 scripts/write-reviewer-risk-register.py

archive-handoff-audit: submission-package-check
	python3 scripts/write-archive-handoff-manifest.py

github-release-asset-audit:
	python3 scripts/audit-github-release-assets.py

github-ci-status-audit:
	python3 scripts/audit-github-ci-status.py

doi-deposit-package: reggov-guidelines-readiness-audit archive-handoff-audit
	python3 scripts/build-doi-deposit-package.py

zenodo-deposit-preflight: doi-deposit-package
	python3 scripts/prepare-zenodo-deposit.py

zenodo-deposit-draft: zenodo-deposit-preflight
	@. ./scripts/load-env.sh; python3 scripts/prepare-zenodo-deposit.py --create-draft

zenodo-deposit-upload: zenodo-deposit-preflight
	@. ./scripts/load-env.sh; python3 scripts/prepare-zenodo-deposit.py --create-draft --upload-package

record-doi-archive:
	@. ./scripts/load-env.sh; python3 scripts/record-doi-archive.py

doi-deposit-readiness-audit: zenodo-deposit-preflight
	python3 scripts/audit-doi-deposit-readiness.py

external-finalization-checklist:
	@. ./scripts/load-env.sh; python3 scripts/write-external-finalization-checklist.py

wiley-submission-form-readiness-audit: submission-package-check
	python3 scripts/audit-wiley-submission-form-readiness.py

reggov-guidelines-readiness-audit: wiley-submission-form-readiness-audit
	python3 scripts/audit-reggov-guidelines-readiness.py

paper-artifacts: campaign mechanism-comparison sensitivity ablation interactions portfolio source-moments source-panel-inventory source-capability-audit dark-money-bridge-audit intermediary-bridge-audit revolving-door-bridge-audit procurement-denominator-audit procurement-modification-composition-audit procurement-benchmark-crosswalk validate validation-scope-coverage claim-boundary-audit claim-source-dependency-audit causal-calibration-targets first-wave-causal-protocols first-wave-source-product-templates first-wave-linkage-candidates first-wave-entity-resolution-seeds first-wave-source-products calibration-queue procurement-refresh-readiness first-wave-source-readiness tables figures paper-build paper-wiley-build paper-supplement-build paper-word-count paper-layout-audit visual-review-checklist latex-log-audit claim-posture-audit calibration-readiness-audit policy-claim-language-audit final-human-readthrough-audit submission-readiness-audit reviewer-risk-register submission-package-build submission-package-check archive-handoff-audit wiley-submission-form-readiness-audit reggov-guidelines-readiness-audit doi-deposit-package doi-deposit-readiness-audit

paper-artifacts-check: paper-artifacts scrub-copy-suffix-artifacts
	python3 scripts/check-paper-artifacts.py

clean: scrub-copy-suffix-artifacts
	rm -rf out
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper/*.pag paper/*.synctex.gz
	rm -f reports/validation-summary.csv reports/validation-summary.md reports/validation-scope-coverage.csv reports/validation-scope-coverage.md reports/substitution-audit.csv reports/substitution-audit.md
	rm -f reports/source-moments.csv reports/source-moments.md reports/source-panel-inventory.csv reports/source-panel-inventory.md reports/source-capability-audit.csv reports/source-capability-audit.md reports/dark-money-bridge-audit.csv reports/dark-money-bridge-audit.md reports/intermediary-bridge-audit.csv reports/intermediary-bridge-audit.md reports/revolving-door-bridge-audit.csv reports/revolving-door-bridge-audit.md reports/procurement-denominator-audit.csv reports/procurement-denominator-audit.md reports/procurement-modification-composition-audit.csv reports/procurement-modification-composition-audit.md reports/procurement-benchmark-crosswalk.csv reports/procurement-benchmark-crosswalk.md reports/procurement-refresh-readiness.csv reports/procurement-refresh-readiness.md reports/claim-boundary-audit.csv reports/claim-boundary-audit.md reports/claim-source-dependency.csv reports/claim-source-dependency.md reports/causal-calibration-targets.csv reports/causal-calibration-targets.md reports/first-wave-causal-protocols.csv reports/first-wave-causal-protocols.md reports/first-wave-source-products.csv reports/first-wave-source-products.md reports/first-wave-linkage-candidates.csv reports/first-wave-linkage-candidate-records.csv reports/first-wave-linkage-candidates.md reports/first-wave-source-readiness.csv reports/first-wave-source-readiness.md reports/claim-posture-audit.csv reports/claim-posture-audit.md reports/paper-layout-audit.md reports/calibration-queue.csv reports/calibration-queue.md
	rm -f reports/calibration-readiness.csv reports/calibration-readiness.md
	rm -f reports/policy-claim-language-audit.csv reports/policy-claim-language-audit.md
	rm -f reports/final-human-readthrough-audit.csv reports/final-human-readthrough-audit.md
	rm -f reports/submission-readiness.csv reports/submission-readiness.md
	rm -f reports/reviewer-risk-register.csv reports/reviewer-risk-register.md
	rm -f reports/archive-handoff-manifest.csv reports/archive-handoff-manifest.json reports/archive-handoff-manifest.md
	rm -f reports/github-release-asset-audit.csv reports/github-release-asset-audit.md
	rm -f reports/github-ci-status-audit.csv reports/github-ci-status-audit.md
	rm -f reports/zenodo-deposit-preflight.csv reports/zenodo-deposit-preflight.md reports/zenodo-draft-deposit.csv reports/zenodo-draft-deposit.md
	rm -f reports/doi-deposit-readiness.csv reports/doi-deposit-readiness.md
	rm -f reports/wiley-submission-form-readiness.csv reports/wiley-submission-form-readiness.md
	rm -f reports/reggov-guidelines-readiness.csv reports/reggov-guidelines-readiness.md
	rm -f reports/latex-log-audit.csv reports/latex-log-audit.md
	rm -f reports/sam-contract-awards-export-audit.csv reports/sam-contract-awards-export-audit.md
	rm -f reports/lobby-capture-mechanism-comparison.csv reports/lobby-capture-mechanism-comparison.md reports/lobby-capture-mechanism-comparison.manifest.json
	rm -f reports/manual-visual-audit.md
	rm -rf docs/source-product-templates/first-wave
	rm -rf dist
