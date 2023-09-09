.PHONY: run-kroki
run-kroki:
	docker-compose -f docs/builder/kroki/docker-compose.yml up --wait

.PHONY: docs
docs:
	make -C docs bpmn-all mmd-all
