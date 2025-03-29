.PHONY: setup setup-circuit test run clean

# Install Python dependencies
setup:
	pip install -r requirements.txt
	@echo "Installation complete. Make sure snarkjs and circom are installed globally."
	@echo "Note: Installation of snarkjs: npm install -g snarkjs"
	@echo "Note: Installation of circom depends on OS. See https://docs.circom.io/getting-started/installation/"
	@echo "To install circuit dependencies, run: make setup-circuit"

# Install circomlib and other circuit dependencies
setup-circuit:
	./init_circuit_deps.sh

# Run tests
test:
	pytest -xvs tests/

# Run the demo with default values
run:
	python -m src.main

# Run the demo with custom values
run-custom:
	python -m src.main --student $(STUDENT) --score-type $(SCORE_TYPE) --score-value $(SCORE_VALUE) --threshold $(THRESHOLD)

# Clean temporary files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	find circuits -type f -name "*.r1cs" -delete
	find circuits -type f -name "*.sym" -delete
	find circuits -type f -name "*.zkey" -delete
	find circuits -type f -name "verification_key.json" -delete
	find circuits -type f -name "witness.wtns" -delete
	find circuits -type f -name "proof.json" -delete
	find circuits -type f -name "public.json" -delete
