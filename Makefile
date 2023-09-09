TAG := $(shell git rev-parse --short HEAD)

.PHONY: image-builder
image-builder:
	docker build -f Dockerfile.kroki . -t docs-builder:$(TAG)
	docker tag docs-builder:$(TAG) docs-builder:latest

bps := $(wildcard docs/business-logic/*)
bpmn_sources := $(foreach bp,$(bps),$(wildcard $(bp)/*.bpmn))
bp_svgs := $(foreach bp,$(bpmn_sources),$(patsubst %.bpmn,%.svg,$(bp)))

.PHONY: $(bp_svgs)
$(bp_svgs): %.svg: %.bpmn
	docker run --rm \
		-u $(shell id -u ${USER}):$(shell id -g ${USER}) \
		-v $(shell pwd)/docs:/docs \
		docs-builder:latest convert /$< -o /$@

.PHONY: bpmn-all
bpmn-all: $(bp_svgs)

.PHONY: docs
docs: bpmn-all
