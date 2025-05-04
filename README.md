# ZKP GPA Verification

A privacy-preserving college admissions system using Zero-Knowledge Proofs. 

## Overview

This project demonstrates how Zero-Knowledge Proofs (ZKPs) can be used to verify a student's academic qualifications (like GPA or SAT scores) without revealing the actual scores. This approach enhances privacy in the college admissions process.

## System Flow

1. Student requests credentials from a Signing Organization.
2. Signing Organization retrieves score data from a Credential Database.
3. Signing Organization provides a signed credential to the student.
4. Student generates a Zero-Knowledge Proof (ZKP) and sends it to the Requesting Institution (university).
5. Requesting Institution verifies the ZKP.
6. Requesting Institution verifies the result with the Signing Organization.

## Prerequisites

- Python 3.8+
- Node.js (for snarkjs)
- Circom (Rust version recommended)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/zkp-gpa-verification.git
cd zkp-gpa-verification

# Install Python dependencies
pip install -r requirements.txt

# Install snarkjs globally
npm install -g snarkjs

# Install Circom (Rust version recommended):
# 1. Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Clone circom repository
git clone https://github.com/iden3/circom.git

# 3. Build circom
cd circom
cargo build --release

# 4. Install circom
cargo install --path circom

# 5. Return to the project directory
cd ..

# Install circomlib (required for the ZKP circuit)
./init_circuit_deps.sh
```

## Usage

### Basic Demo

```bash
# Run the basic demo
python -m src.main
```

### Interactive Demo (For Presentations)

```bash
# Run the interactive demo
./scripts/run_demo.sh

# Or directly with Python
python -m src.interactive_demo
```

The interactive demo provides a role-based interface that lets you:
- Switch between Student, School, and University perspectives
- Understand how each party interacts with the system
- Visualize the complete flow of the zero-knowledge proof process
- See how privacy is preserved throughout the verification

## Project Structure

- `src/`: Source code for the ZKP system
  - `student/`: Student-related components
  - `signing_org/`: Signing Organization components
  - `institution/`: Requesting Institution components
  - `credential_db/`: Credential Database components
  - `common/`: Shared utilities
- `circuits/`: Circom circuits for ZKP
- `tests/`: Test cases
- `docs/`: Additional documentation

## Contributors

- Ashutosh Sahu
- Andy Zhao
- Caiqing Shen
- Jessica Chan
