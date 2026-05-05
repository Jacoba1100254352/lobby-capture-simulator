JAVAC ?= javac
JAVA ?= java
REPORT_GENERATED_AT ?= 2026-05-05T00:00:00Z
REPORT_GIT_COMMIT ?= tracked-artifact-build
REPORT_GIT_DIRTY ?= false
REPORT_ENV := LOBBY_CAPTURE_REPORT_TIMESTAMP=$(REPORT_GENERATED_AT) LOBBY_CAPTURE_REPORT_GIT_COMMIT=$(REPORT_GIT_COMMIT) LOBBY_CAPTURE_REPORT_WORKING_TREE_DIRTY=$(REPORT_GIT_DIRTY)

MAIN_SOURCES := $(shell find src/main/java -name "*.java" | sort)
TEST_SOURCES := $(shell find src/test/java -name "*.java" | sort)
MAIN_CLASS := lobbycapture.Main
TEST_CLASSES := lobbycapture.SmokeTest lobbycapture.AdaptationTest

.PHONY: compile test run campaign sensitivity ablation interactions source-moments calibration-queue validate snapshot-2024-env tables figures paper paper-word-count wiley-template wiley-tex-deps paper-wiley submission-package paper-artifacts paper-artifacts-check clean

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

sensitivity: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --sensitivity --runs 30 --contests 70 --seed 142

ablation: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --ablation --runs 40 --contests 80 --seed 242

interactions: compile
	$(REPORT_ENV) $(JAVA) -cp out/classes $(MAIN_CLASS) --interactions --runs 25 --contests 60 --seed 342

source-moments:
	python3 scripts/extract-source-moments.py

calibration-queue: validate
	python3 scripts/classify-validation-misses.py

validate: source-moments
	python3 scripts/validate-reports.py

snapshot-2024-env:
	python3 scripts/create-2024-env-snapshot.py

tables:
	python3 scripts/generate-paper-tables.py

figures:
	python3 scripts/generate-interaction-figures.py

paper: tables figures
	rm -f paper/main.aux paper/main.bbl paper/main.blg
	cd paper && pdflatex -interaction=nonstopmode main.tex
	cd paper && bibtex main
	cd paper && pdflatex -interaction=nonstopmode main.tex
	cd paper && pdflatex -interaction=nonstopmode main.tex
	cd paper && pdflatex -interaction=nonstopmode main.tex

paper-word-count:
	python3 scripts/check-paper-word-count.py

wiley-template:
	./scripts/fetch-wiley-template.sh

wiley-tex-deps:
	./scripts/install-wiley-tex-deps.sh

paper-wiley: tables figures wiley-template
	./scripts/build-wiley-paper.sh

submission-package: paper-wiley paper-word-count
	./scripts/build-submission-package.sh

paper-artifacts: campaign sensitivity ablation interactions source-moments validate calibration-queue tables figures paper paper-wiley submission-package paper-word-count

paper-artifacts-check: paper-artifacts
	python3 scripts/check-paper-artifacts.py

clean:
	rm -rf out
	rm -f paper/*.aux paper/*.bbl paper/*.blg paper/*.log paper/*.out paper/*.pdf paper/*.pag paper/*.synctex.gz
	rm -f reports/validation-summary.csv reports/validation-summary.md reports/substitution-audit.csv reports/substitution-audit.md
	rm -f reports/source-moments.csv reports/source-moments.md reports/calibration-queue.csv reports/calibration-queue.md
	rm -rf dist
