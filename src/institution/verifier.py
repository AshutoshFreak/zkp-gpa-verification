#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Verifier module for the ZKP GPA verification system.

This module represents the requesting institution (university) that verifies proofs.
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
from ..signing_org.credential_issuer import CredentialIssuer


class ProofVerifier:
    """Represents the university that verifies zero-knowledge proofs."""

    def __init__(
        self, 
        institution_name: str,
        trusted_issuers: Optional[Dict[str, str]] = None,
        data_dir: Optional[str] = None
    ):
        """
        Initialize the proof verifier.

        Args:
            institution_name: Name of the institution
            trusted_issuers: Dictionary of trusted issuer names and their public key paths
            data_dir: Directory to store verification data (default: create new one)
        """
        self.institution_name = institution_name
        
        # Set up data directory
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path.home() / ".zkp_gpa_verification" / "institutions" / institution_name
            
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Dictionary to store trusted issuers' public keys
        self.trusted_issuers = {}
        
        # Load trusted issuers
        if trusted_issuers:
            for issuer_name, key_path in trusted_issuers.items():
                try:
                    self.trusted_issuers[issuer_name] = CryptoUtils.load_public_key(key_path)
                except Exception as e:
                    logging.error(f"Error loading public key for {issuer_name}: {e}")

    def add_trusted_issuer(self, issuer_name: str, public_key_path: str) -> bool:
        """
        Add a trusted credential issuer.

        Args:
            issuer_name: Name of the issuer
            public_key_path: Path to the issuer's public key

        Returns:
            True if the issuer was added successfully, False otherwise
        """
        try:
            public_key = CryptoUtils.load_public_key(public_key_path)
            self.trusted_issuers[issuer_name] = public_key
            return True
        except Exception as e:
            logging.error(f"Error adding trusted issuer {issuer_name}: {e}")
            return False

    def verify_proof(
        self, 
        proof_data: Dict[str, Any],
        verification_key_path: str,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Verify a zero-knowledge proof.

        Args:
            proof_data: The proof data to verify
            verification_key_path: Path to the verification key
            threshold: The threshold to verify (default: use value from proof)

        Returns:
            Dictionary with verification results
        """
        # Check ZKP dependencies
        dependencies = ZKPUtils.check_dependencies()
        if not dependencies["snarkjs"]:
            return {
                "valid": False,
                "error": "Missing dependency: snarkjs not installed"
            }
            
        # Extract metadata
        metadata = proof_data.get("metadata", {})
        proof_threshold = metadata.get("threshold")
        scale_factor = metadata.get("scale_factor", 100)  # Default to 100 if not specified
        
        # Use provided threshold or fall back to the one in the proof
        if threshold is None:
            threshold = proof_threshold
        elif threshold != proof_threshold:
            return {
                "valid": False,
                "error": f"Threshold mismatch: proof was generated for {proof_threshold}, but verifying against {threshold}"
            }
            
        # Create temporary files for proof verification
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as proof_file:
            json.dump(proof_data["proof"], proof_file)
            proof_path = proof_file.name
            
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as public_file:
            json.dump(proof_data["public"], public_file)
            public_path = public_file.name
            
        try:
            # Verify the ZKP
            is_valid = ZKPUtils.verify_proof(verification_key_path, proof_path, public_path)
            
            if not is_valid:
                return {
                    "valid": False,
                    "error": "Invalid zero-knowledge proof"
                }
                
            # If we get here, the proof is valid
            score_type = metadata.get('score_type', 'score')
            
            return {
                "valid": True,
                "metadata": metadata,
                "message": f"Score for {score_type} is{' ' if is_valid else ' not '}above threshold {threshold}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error verifying proof: {e}"
            }
        finally:
            # Clean up temporary files
            try:
                os.unlink(proof_path)
                os.unlink(public_path)
            except:
                pass

    def verify_with_issuer(
        self, 
        proof_data: Dict[str, Any],
        issuer: CredentialIssuer
    ) -> Dict[str, Any]:
        """
        Verify a proof result with the issuing organization.

        Args:
            proof_data: The proof data to verify
            issuer: The credential issuer to verify with

        Returns:
            Dictionary with verification results
        """
        metadata = proof_data.get("metadata", {})
        credential_id = metadata.get("credential_id")
        issuer_name = metadata.get("credential_issuer")
        
        if issuer.name != issuer_name:
            return {
                "valid": False,
                "error": f"Issuer mismatch: proof was issued by {issuer_name}, but verifying with {issuer.name}"
            }
            
        # In a real system, we would query the issuer to verify the credential
        # For this demo, we'll just simulate the verification
        
        return {
            "valid": True,
            "message": f"Credential {credential_id} verified with issuer {issuer_name}"
        }
