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

short_hash = $(shell hashdeep -r -l $(1) | sort | md5sum | grep -Eo '^[0-9a-z]{6}')
time = $(shell date +%s | grep -Eo '[0-9]{6}$$')

.PHONY: bebr
bebr:
	@echo $(call time)

init_hash=$(call short_hash,./test/init)
pg_time=$(call time)
.PHONY: pg-image
pg-image:
	docker build -f test/Dockerfile.pg \
		--build-arg INIT=test/init \
		-t pgtest:${init_hash}-${pg_time} .
	docker tag pgtest:${init_hash}-${pg_time} pgtest:latest

PB_ABS := "https://github.com/protocolbuffers/protobuf/releases"
PROTOC_VERSION := "24.4"
PROTOC_ARCHIVE := "protoc-${PROTOC_VERSION}-linux-x86_64.zip"
PB_REL := "download/v${PROTOC_VERSION}/${PROTOC_ARCHIVE}"
PB_PATH = ${PB_ABS}/${PB_REL}

.PHONY: install-protoc
install-protoc:
	curl -LO ${PB_PATH}
	unzip ${PROTOC_ARCHIVE} -d ${HOME}/.local
	rm ${PROTOC_ARCHIVE}

.PHONY: python-gen
python-gen:
	poetry run python3 -m grpc_tools.protoc \
		-I./api --python_out=./api \
		--pyi_out=./api \
		--grpc_python_out=./api \
		./api/apiv1.proto 
