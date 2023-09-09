TAG := $(shell git rev-parse --short HEAD)

.PHONY: image-builder
image-builder:
	docker build -f Dockerfile.kroki . -t docs-builder:$(TAG)
	docker tag docs-builder:$(TAG) docs-builder:latest

bps := $(filter-out Makefile,$(wildcard docs/business-logic/*))
bpmn_sources := $(foreach bp,$(bps),$(wildcard $(bp)/*.bpmn))
bp_svgs := $(foreach bp,$(bpmn_sources),$(patsubst %.bpmn,%.svg,$(bp)))
mmd_sources := docs/hld/system.md
mmd_pngs := $(foreach mmd,$(mmd_sources),$(patsubst %.md,%.png,$(mmd)))

.PHONY: $(bp_svgs)
$(bp_svgs): %.svg: %.bpmn
	docker run --rm -v $(pwd)/docs:/docs docs-builder:latest \
		convert $< -o $@

.PHONY: $(mmd_pngs)
$(mmd_pngs): %.png: %.md
	docker run --rm -v $(pwd)/docs:/docs docs-builder:latest \
		convert $< -o $@

.PHONY: bpmn-all
bpmn-all: $(bp_svgs)

.PHONY: mmd-all
mmd-all: $(mmd_pngs)

.PHONY: docs
docs: bpmn-all mmd-all
