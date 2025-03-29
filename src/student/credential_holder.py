#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Credential holder module for the ZKP GPA verification system.

This module represents the student who holds credentials and generates proofs.
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import from common module
from ..common.zkp_utils import ZKPUtils
from ..common.crypto_utils import CryptoUtils


class CredentialHolder:
    """Represents a student who holds credentials and generates proofs."""

    def __init__(self, student_id: str, data_dir: Optional[str] = None):
        """
        Initialize the credential holder.

        Args:
            student_id: Unique identifier for the student
            data_dir: Directory to store credentials and proofs (default: create new one)
        """
        self.student_id = student_id
        
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path.home() / ".zkp_gpa_verification" / "students" / student_id
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Directories for storing credentials and proofs
        self.credentials_dir = self.data_dir / "credentials"
        self.proofs_dir = self.data_dir / "proofs"
        
        self.credentials_dir.mkdir(exist_ok=True)
        self.proofs_dir.mkdir(exist_ok=True)
        
        # Dictionary to store credentials in memory
        self._credentials = {}
        self._load_credentials()

    def _load_credentials(self) -> None:
        """
        Load credentials from files.
        
        Returns:
            None
        """
        for credential_file in self.credentials_dir.glob("*.json"):
            try:
                with open(credential_file, 'r') as f:
                    credential_data = json.load(f)
                    
                credential_id = credential_data.get("credential", {}).get("credential_id")
                if credential_id:
                    self._credentials[credential_id] = credential_data
            except (json.JSONDecodeError, KeyError) as e:
                logging.warning(f"Error loading credential from {credential_file}: {e}")

    def store_credential(self, credential_data: Dict[str, Any]) -> bool:
        """
        Store a credential received from a signing organization.

        Args:
            credential_data: The credential data with signature

        Returns:
            True if the credential was stored successfully, False otherwise
        """
        try:
            credential = credential_data["credential"]
            signature = credential_data["signature"]
            credential_id = credential["credential_id"]
            
            # Save to file
            credential_path = self.credentials_dir / f"{credential_id}.json"
            with open(credential_path, 'w') as f:
                json.dump(credential_data, f, indent=2)
                
            # Store in memory
            self._credentials[credential_id] = credential_data
            
            return True
        except (KeyError, IOError) as e:
            logging.error(f"Error storing credential: {e}")
            return False

    def list_credentials(self) -> List[Dict[str, Any]]:
        """
        List all stored credentials.

        Returns:
            List of credential data dictionaries
        """
        return list(self._credentials.values())

    def get_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific credential by ID.

        Args:
            credential_id: The ID of the credential to get

        Returns:
            The credential data, or None if not found
        """
        return self._credentials.get(credential_id)

    def generate_proof(
        self, 
        credential_id: str, 
        threshold: float,
        circuit_path: str,
        verification_key_path: Optional[str] = None,
        scale_factor: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a zero-knowledge proof that a score exceeds a threshold.

        Args:
            credential_id: The ID of the credential to use
            threshold: The threshold value to prove against
            circuit_path: Path to the circom circuit file
            verification_key_path: Path to the verification key file (default: None)
            scale_factor: Factor to scale decimal values to integers (default: 100)

        Returns:
            Dictionary with proof data, or None if generation failed
        """
        # Get the credential
        credential_data = self.get_credential(credential_id)
        if not credential_data:
            logging.error(f"Credential {credential_id} not found")
            return None
            
        credential = credential_data["credential"]
        signature = credential_data["signature"]
        
        # Extract the score value and convert to integer
        score_value = credential["score_value"]
        
        # Scale values to integers for ZKP circuit
        score_int = int(score_value * scale_factor)
        threshold_int = int(threshold * scale_factor)
        
        # Log the converted values
        logging.info(f"Converting score {score_value} to integer {score_int}")
        logging.info(f"Converting threshold {threshold} to integer {threshold_int}")
        
        # Check for snarkjs dependency
        dependencies = ZKPUtils.check_dependencies()
        if not dependencies["snarkjs"]:
            logging.error("Missing dependency: snarkjs not installed")
            return None
            
        # Prepare output directory
        proof_dir = self.proofs_dir / credential_id
        proof_dir.mkdir(exist_ok=True)
        
        try:
            # Compile the circuit if needed
            compiled = ZKPUtils.compile_circuit(circuit_path, str(proof_dir))
            
            # Set up the circuit
            setup = ZKPUtils.setup_circuit(compiled["r1cs"], str(proof_dir))
            
            # Prepare the input for the circuit - use scaled integer values
            input_data = {
                "score": score_int,
                "threshold": threshold_int
            }
            
            # Generate the witness
            witness_path = ZKPUtils.generate_witness(compiled["wasm"], input_data, str(proof_dir))
            
            # Generate the proof
            proof_files = ZKPUtils.generate_proof(setup["zkey"], witness_path, str(proof_dir))
            
            # Get the verification key path
            if not verification_key_path:
                verification_key_path = setup["verification_key"]
                
            # Create simplified proof for transmission
            proof_data = ZKPUtils.simplify_proof(proof_files["proof"], proof_files["public"])
            
            # Add metadata to the proof (use original floating point values in metadata)
            proof_data["metadata"] = {
                "credential_id": credential_id,
                "credential_issuer": credential["issuer"],
                "score_type": credential["score_type"],
                "threshold": threshold,
                "student_id": self.student_id,
                "scale_factor": scale_factor
            }
            
            # Save the full proof
            full_proof_path = proof_dir / "full_proof.json"
            with open(full_proof_path, 'w') as f:
                json.dump(proof_data, f, indent=2)
                
            return proof_data
        except Exception as e:
            logging.error(f"Error generating proof: {e}")
            return None
