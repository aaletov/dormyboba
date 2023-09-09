bps := $(filter-out Makefile,$(wildcard business-logic/*))
bpmn_sources := $(foreach bp,$(bps),$(wildcard $(bp)/*.bpmn))
bp_svgs := $(foreach bp,$(bpmn_sources),$(patsubst %.bpmn,%.svg,$(bp)))
mmd_sources := hld/system.md
mmd_pngs := $(foreach mmd,$(mmd_sources),$(patsubst %.md,%.png,$(mmd)))

.PHONY: $(bp_svgs)
$(bp_svgs): %.svg: %.bpmn
ifeq ($(shell docker-compose ls | grep 'kroki'),)
	$(error kroki isn't running)
endif
	python3 builder/builder.py -t bpmn -f $< -o $@

.PHONY: $(mmd_pngs)
$(mmd_pngs): %.png: %.md
ifeq ($(shell docker-compose ls | grep 'kroki'),)
	$(error kroki isn't running)
endif
	python3 builder/builder.py -t mermaid -f $< -o $@

.PHONY: bpmn-all
bpmn-all: $(bp_svgs)

.PHONY: mmd-all
mmd-all: $(mmd_pngs)
