.PHONY: all install test validate bfo owl demo clean

all: owl validate test demo

install:
	pip install -e ".[dev]"

owl:            ## regenerate the OWL module from data/kernel.json
	python tools/build_owl.py
	cp data/kernel.json src/rkernel/data/kernel.json

validate:       ## kernel, schemas, OWL agreement, reasoning, and inference
	PYTHONPATH=src python -m rkernel.cli validate

bfo:            ## check the alignment to the real BFO, IAO and RO
	@# Set RK_BFO_DIR to resolve the imports from disk instead of the network.
	python tools/check_bfo.py $(if $(RK_BFO_DIR),--local $(RK_BFO_DIR),)

test:
	PYTHONPATH=src python -m pytest tests -q

demo:           ## regenerate everything in out/
	python examples/run_all.py

clean:
	rm -rf out/* .pytest_cache **/__pycache__
