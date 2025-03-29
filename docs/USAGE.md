# Using the ZKP GPA Verification System

This document explains how to use the ZKP GPA Verification System.

## Prerequisites

Before you begin, ensure you have installed:

1. Python 3.8 or higher
2. Node.js (for snarkjs)
3. Circom (for compiling ZK circuits)

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

## Running the Demo

The simplest way to run the demo is with the default values:

```bash
python -m src.main
```

This will run through the entire flow of the system:

1. Setting up a credential database
2. Creating a signing organization
3. Issuing a credential to a student
4. Generating a zero-knowledge proof
5. Verifying the proof by a university
6. Verifying the result with the signing organization

### Custom Demo Parameters

You can customize the demo with the following parameters:

```bash
python -m src.main --student "student123" --score-type "gpa" --score-value 3.8 --threshold 3.5
```

Or using the Makefile:

```bash
make run-custom STUDENT=student123 SCORE_TYPE=gpa SCORE_VALUE=3.8 THRESHOLD=3.5
```

## Using the Components Individually

### Credential Database

```python
from src.credential_db.database import CredentialDatabase

# Create or load a database
db = CredentialDatabase()

# Add a student with scores
db.add_student("student123", {"gpa": 3.8, "sat": 1450})

# Get a student's scores
scores = db.get_student_scores("student123")
print(scores)  # {"gpa": 3.8, "sat": 1450}

# Update a student's scores
db.update_student_scores("student123", {"gpa": 3.9})
```

### Signing Organization

```python
from src.credential_db.database import CredentialDatabase
from src.signing_org.credential_issuer import CredentialIssuer

# Create a database and add a student
db = CredentialDatabase()
db.add_student("student123", {"gpa": 3.8})

# Create a signing organization
issuer = CredentialIssuer("MySchool", credential_db=db)

# Issue a credential
credential = issuer.issue_credential("student123", "gpa")

# Get the public key path
public_key_path = issuer.get_public_key_path()
```

### Student

```python
from src.student.credential_holder import CredentialHolder

# Create a student
student = CredentialHolder("student123")

# Store a credential
student.store_credential(credential)

# List credentials
credentials = student.list_credentials()

# Generate a proof
proof_data = student.generate_proof(
    credential_id=credential["credential"]["credential_id"],
    threshold=3.5,
    circuit_path="circuits/threshold_check.circom"
)
```

### University

```python
from src.institution.verifier import ProofVerifier

# Create a university
university = ProofVerifier("MyUniversity")

# Add a trusted issuer
university.add_trusted_issuer("MySchool", public_key_path)

# Verify a proof
verification_result = university.verify_proof(
    proof_data=proof_data,
    verification_key_path="path/to/verification_key.json",
    threshold=3.5
)

# Verify with the issuing organization
issuer_verification = university.verify_with_issuer(proof_data, issuer)
```

## Testing

Run the tests to ensure everything is working correctly:

```bash
pytest -xvs tests/
```

Or using the Makefile:

```bash
make test
```

## Cleaning Up

To clean temporary files:

```bash
make clean
```
