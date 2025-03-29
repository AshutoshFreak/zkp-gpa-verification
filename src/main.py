#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main module for the ZKP GPA verification system.

This script demonstrates the complete flow of the system:
1. Student requests credentials from a Signing Organization
2. Signing Organization retrieves score data from a Credential Database
3. Signing Organization issues signed credentials to students
4. Student generates a Zero-Knowledge Proof (ZKP) and sends it to the Requesting Institution
5. Requesting Institution verifies the ZKP
6. Requesting Institution verifies the result with the Signing Organization
"""

import os
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Import components
from .credential_db.database import CredentialDatabase
from .signing_org.credential_issuer import CredentialIssuer
from .student.credential_holder import CredentialHolder
from .institution.verifier import ProofVerifier
from .common.zkp_utils import ZKPUtils


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def demo_complete_flow(
    student_id: str,
    score_type: str,
    score_value: float,
    threshold: float,
    circuit_path: str
) -> None:
    """
    Demonstrate the complete flow of the ZKP GPA verification system.

    Args:
        student_id: ID of the student
        score_type: Type of score (e.g., "gpa", "sat")
        score_value: Value of the score
        threshold: Threshold value for verification
        circuit_path: Path to the circom circuit file

    Returns:
        None
    """
    print("\n=== ZKP GPA Verification System Demo ===\n")
    
    # Check for snarkjs dependency
    dependencies = ZKPUtils.check_dependencies()
    if not dependencies["snarkjs"]:
        print("Error: Missing dependency. Please install snarkjs first.")
        print("  npm install -g snarkjs")
        return
        
    # Check for circomlib
    circuit_dir = Path(circuit_path).parent
    node_modules = circuit_dir / "node_modules"
    # circomlib = node_modules / "circomlib"
    # if not circomlib.exists():
    #     print("\nError: circomlib not found in node_modules directory.")
    #     print("Please run the initialization script to install it:")
    #     print("  ./init_circuit_deps.sh")
    #     return
        
    # 1. Set up the credential database
    print("\n1. Setting up credential database...")
    db = CredentialDatabase()
    
    # Add or update the student's score
    if db.has_student(student_id):
        db.update_student_scores(student_id, {score_type: score_value})
        print(f"  Updated scores for student {student_id}")
    else:
        db.add_student(student_id, {score_type: score_value})
        print(f"  Added student {student_id} with {score_type} score of {score_value}")
    
    # 2. Set up the signing organization
    print("\n2. Setting up signing organization...")
    issuer = CredentialIssuer("ExampleSchool", credential_db=db)
    print(f"  Signing organization 'ExampleSchool' initialized")
    print(f"  Public key path: {issuer.get_public_key_path()}")
    
    # 3. Student requests and receives credential
    print("\n3. Student requests credential from signing organization...")
    credential = issuer.issue_credential(student_id, score_type)
    if not credential:
        print(f"  Error: Failed to issue credential for student {student_id}")
        return
        
    print(f"  Credential issued for {score_type} score")
    
    # 4. Student creates a credential holder and stores the credential
    print("\n4. Student receives and stores the credential...")
    student = CredentialHolder(student_id)
    student.store_credential(credential)
    print(f"  Credential stored by student {student_id}")
    
    # 5. Student generates a zero-knowledge proof
    print("\n5. Student generates a zero-knowledge proof...")
    credential_id = credential["credential"]["credential_id"]
    proof_data = student.generate_proof(credential_id, threshold, circuit_path)
    if not proof_data:
        print(f"  Error: Failed to generate proof")
        return
        
    print(f"  Zero-knowledge proof generated for threshold {threshold}")
    
    # 6. University verifies the proof
    print("\n6. University verifies the proof...")
    university = ProofVerifier("ExampleUniversity")
    university.add_trusted_issuer("ExampleSchool", issuer.get_public_key_path())
    
    # Get the verification key path from the proof metadata directory
    student_proof_dir = Path.home() / ".zkp_gpa_verification" / "students" / student_id / "proofs" / credential_id
    verification_key_path = str(student_proof_dir / "verification_key.json")
    
    verification_result = university.verify_proof(proof_data, verification_key_path, threshold)
    if not verification_result["valid"]:
        print(f"  Error: {verification_result.get('error', 'Proof verification failed')}")
        return
        
    print(f"  Proof verification result: {verification_result['message']}")
    
    # 7. University verifies with the issuing organization
    print("\n7. University verifies with the issuing organization...")
    issuer_verification = university.verify_with_issuer(proof_data, issuer)
    if not issuer_verification["valid"]:
        print(f"  Error: {issuer_verification.get('error', 'Issuer verification failed')}")
        return
        
    print(f"  Issuer verification result: {issuer_verification['message']}")
    
    print("\n=== Demo completed successfully ===")
    print(f"Student {student_id} has successfully proven that their {score_type} score")
    print(f"is above the threshold of {threshold} without revealing the actual score ({score_value}).\n")


def main() -> None:
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description='ZKP GPA Verification System Demo')
    parser.add_argument('--student', type=str, default="student123", help='Student ID')
    parser.add_argument('--score-type', type=str, default="gpa", help='Score type (e.g., gpa, sat)')
    parser.add_argument('--score-value', type=float, default=3.8, help='Score value')
    parser.add_argument('--threshold', type=float, default=3.5, help='Threshold value')
    parser.add_argument('--circuit', type=str, default=None, help='Path to the circom circuit file')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Get the path to the threshold_check circuit
    if args.circuit:
        circuit_path = args.circuit
    else:
        # Default path is in the circuits directory
        script_dir = Path(__file__).parent.parent
        circuit_path = str(script_dir / "circuits" / "threshold_check.circom")
    
    # Run the complete flow demo
    demo_complete_flow(
        student_id=args.student,
        score_type=args.score_type,
        score_value=args.score_value,
        threshold=args.threshold,
        circuit_path=circuit_path
    )


if __name__ == "__main__":
    main()
