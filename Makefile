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

.PHONY: compile test run campaign mechanism-comparison sensitivity ablation interactions portfolio source-moments source-panel-inventory claim-boundary-audit claim-source-dependency-audit claim-posture-audit calibration-queue validate snapshot-2024-env tables figures paper paper-build paper-supplement-build paper-supplement paper-word-count wiley-template wiley-tex-deps paper-wiley paper-wiley-build submission-package submission-package-build submission-package-check paper-layout-audit visual-review-checklist paper-artifacts paper-artifacts-check clean

compile:
	@mkdir -p out/classes
	$(JAVAC) -d out/classes $(MAIN_SOURCES)

test: compile
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

calibration-queue: validate
	python3 scripts/classify-validation-misses.py

validate: source-moments source-panel-inventory
	python3 scripts/validate-reports.py

claim-boundary-audit: validate
	python3 scripts/audit-claim-boundaries.py

claim-source-dependency-audit: claim-boundary-audit
	python3 scripts/audit-claim-dependencies.py

snapshot-2024-env:
	python3 scripts/create-2024-env-snapshot.py

tables: claim-source-dependency-audit
	python3 scripts/generate-paper-tables.py

figures: claim-boundary-audit
	python3 scripts/generate-interaction-figures.py

paper-build:
	rm -f paper/$(PAPER_BASENAME).aux paper/$(PAPER_BASENAME).bbl paper/$(PAPER_BASENAME).blg
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(BIBTEX) $(PAPER_BASENAME)
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex
	cd paper && $(PDFLATEX) -interaction=nonstopmode $(PAPER_BASENAME).tex

paper-supplement-build:
	find paper -maxdepth 1 -type f -name 'supplement [0-9]*.aux' -exec rm -f {} +
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

paper-wiley-build: wiley-template
	./scripts/build-wiley-paper.sh

paper-wiley: tables figures paper-wiley-build

submission-package-build:
	./scripts/build-submission-package.sh

submission-package-check: submission-package-build
	./scripts/check-submission-package.sh

submission-package: paper-wiley paper-supplement paper-word-count visual-review-checklist submission-package-build submission-package-check

paper-layout-audit: paper-build paper-wiley-build paper-supplement-build
	python3 scripts/audit-paper-layout.py

visual-review-checklist: paper-layout-audit
	python3 scripts/write-visual-review-checklist.py

claim-posture-audit: claim-boundary-audit claim-source-dependency-audit calibration-queue visual-review-checklist
	python3 scripts/audit-claim-posture.py

paper-artifacts: campaign mechanism-comparison sensitivity ablation interactions portfolio source-moments source-panel-inventory validate claim-boundary-audit claim-source-dependency-audit calibration-queue tables figures paper-build paper-wiley-build paper-supplement-build paper-word-count paper-layout-audit visual-review-checklist claim-posture-audit submission-package-build submission-package-check

paper-artifacts-check: paper-artifacts
	python3 scripts/check-paper-artifacts.py

clean:
	rm -rf out
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper/*.pag paper/*.synctex.gz
	rm -f reports/validation-summary.csv reports/validation-summary.md reports/substitution-audit.csv reports/substitution-audit.md
	rm -f reports/source-moments.csv reports/source-moments.md reports/source-panel-inventory.csv reports/source-panel-inventory.md reports/claim-boundary-audit.csv reports/claim-boundary-audit.md reports/claim-source-dependency.csv reports/claim-source-dependency.md reports/claim-posture-audit.csv reports/claim-posture-audit.md reports/paper-layout-audit.md reports/calibration-queue.csv reports/calibration-queue.md
	rm -f reports/lobby-capture-mechanism-comparison.csv reports/lobby-capture-mechanism-comparison.md reports/lobby-capture-mechanism-comparison.manifest.json
	rm -f reports/manual-visual-audit.md
	rm -rf dist
