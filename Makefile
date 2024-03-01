KROKI_CLI_IMAGE := "aapozd/kroki-cli:0.5.0-alpine3.17"
TAG := $(shell git rev-parse --short HEAD)

.PHONY: pull-kroki-cli-image
image-builder:
	docker pull ${KROKI_CLI_IMAGE}

bps := $(wildcard docs/business-logic/*)
bpmn_sources := $(foreach bp,$(bps),$(wildcard $(bp)/*.bpmn))
bp_svgs := $(foreach bp,$(bpmn_sources),$(patsubst %.bpmn,%.svg,$(bp)))
puml_sources := $(wildcard docs/hld/*.puml)
hld_svgs := $(foreach puml,$(puml_sources),$(patsubst %.puml,%.svg,$(puml)))

$(bp_svgs): %.svg: %.bpmn
	docker run --rm \
		-u $(shell id -u ${USER}):$(shell id -g ${USER}) \
		-v $(shell pwd)/docs:/docs \
		${KROKI_CLI_IMAGE} convert /$< -o /$@

$(hld_svgs): %.svg: %.puml
	docker run --rm \
		-u $(shell id -u ${USER}):$(shell id -g ${USER}) \
		-v $(shell pwd)/docs:/docs \
		${KROKI_CLI_IMAGE} convert /$< -o /$@

.PHONY: bpmn-all
bpmn-all: $(bp_svgs)

.PHONY: puml-all
puml-all: $(hld_svgs)

.PHONY: docs
docs: bpmn-all puml-all

image_time=$(shell git rev-parse --short HEAD)
.PHONY: docker-image
docker-image:
	docker build -t dormyboba:${image_time} .
	docker tag dormyboba:${image_time} dormyboba:latest
