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

init_hash=$(call short_hash,./test/init)
pg_time=$(call time)
.PHONY: pg-image
pg-image:
	docker build -f test/Dockerfile.pg \
		--build-arg INIT=test/init \
		-t pgtest:${init_hash}-${pg_time} .
	docker tag pgtest:${init_hash}-${pg_time} pgtest:latest

PG_USER := postgres
PG_PASSWORD := 123456
PG_HOST := postgresql
PG_PORT := 5432
PG_DB := dormyboba
ALCH_URL := postgresql://${PG_USER}:${PG_PASSWORD}@${PG_HOST}:${PG_PORT}/${PG_DB}

.PHONY: alchemy-models
alchemy-models:
	poetry run sqlacodegen ${ALCH_URL} --outfile dormyboba/model/generated.py
