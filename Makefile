.PHONY: check-hub inventory

check-hub:
	python3 04_code/validate_hub.py

inventory:
	python3 04_code/00_inventory.py --output 05_results/artifact_inventory.json
