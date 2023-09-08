bps := $(filter-out Makefile,$(wildcard business-logic/*))
bpmn_sources := $(foreach bp,$(bps),$(wildcard $(bp)/*.bpmn))
bp_svgs := $(foreach bp,$(bpmn_sources),$(patsubst %.bpmn,%.svg,$(bp)))

.PHONY: run-kroki
run-kroki:
	docker-compose -f builder/kroki/docker-compose.yml up --wait

.PHONY: $(bp_svgs)
$(bp_svgs): %.svg: %.bpmn
ifeq ($(shell docker-compose ls | grep 'kroki'),)
	$(error kroki isn't running)
endif
	python3 builder/builder.py -t bpmn -f $< -o $@

bpmn-all: $(bp_svgs)
