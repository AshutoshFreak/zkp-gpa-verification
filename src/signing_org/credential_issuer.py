#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Credential issuer module for the ZKP GPA verification system.

This module represents the signing organization that issues signed credentials.
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import from common module
from ..common.crypto_utils import CryptoUtils
from ..credential_db.database import CredentialDatabase


class CredentialIssuer:
    """Represents the signing organization that issues signed credentials."""

    def __init__(
        self, 
        name: str,
        private_key_path: Optional[str] = None,
        public_key_path: Optional[str] = None,
        key_password: Optional[str] = None,
        credential_db: Optional[CredentialDatabase] = None
    ):
        """
        Initialize the credential issuer.

        Args:
            name: Name of the signing organization
            private_key_path: Path to the organization's private key (default: generate new key)
            public_key_path: Path to the organization's public key (default: generate new key)
            key_password: Password for the private key (default: None)
            credential_db: Credential database instance (default: create new one)
        """
        self.name = name
        
        # Create or load keys
        if private_key_path and public_key_path and os.path.exists(private_key_path) and os.path.exists(public_key_path):
            self.private_key = CryptoUtils.load_private_key(private_key_path, key_password)
            self.public_key = CryptoUtils.load_public_key(public_key_path)
        else:
            # Generate new keys
            keys_dir = Path.home() / ".zkp_gpa_verification" / "keys" / name
            keys_dir.mkdir(parents=True, exist_ok=True)
            
            private_key_path = str(keys_dir / "private_key.pem")
            public_key_path = str(keys_dir / "public_key.pem")
            
            if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
                logging.info(f"Generating new keys for {name}")
                self.private_key, self.public_key = CryptoUtils.generate_key_pair()
                CryptoUtils.save_private_key(self.private_key, private_key_path, key_password)
                CryptoUtils.save_public_key(self.public_key, public_key_path)
            else:
                self.private_key = CryptoUtils.load_private_key(private_key_path, key_password)
                self.public_key = CryptoUtils.load_public_key(public_key_path)
                
        self.private_key_path = private_key_path
        self.public_key_path = public_key_path
        
        # Set up credential database
        self.credential_db = credential_db if credential_db else CredentialDatabase()

    def issue_credential(
        self, 
        student_id: str, 
        score_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Issue a signed credential for a student's score.

        Args:
            student_id: Unique identifier for the student
            score_type: Type of score to include in the credential (e.g., "gpa", "sat")

        Returns:
            Dictionary with the signed credential, or None if student/score not found
        """
        # Get the student's scores
        scores = self.credential_db.get_student_scores(student_id)
        if not scores:
            logging.warning(f"No scores found for student {student_id}")
            return None
            
        if score_type not in scores:
            logging.warning(f"Score type {score_type} not found for student {student_id}")
            return None
            
        # Create the credential
        credential_id = str(uuid.uuid4())
        score_value = scores[score_type]
        
        credential_data = {
            "credential_id": credential_id,
            "issuer": self.name,
            "issued_to": student_id,
            "score_type": score_type,
            "score_value": score_value,
            "issued_at": int(os.path.getmtime(self.public_key_path))  # Use key file timestamp for demo
        }
        
        # Sign the credential
        signature = CryptoUtils.sign_data(self.private_key, credential_data)
        
        # Return the signed credential
        return {
            "credential": credential_data,
            "signature": signature
        }

    def verify_credential(
        self, 
        credential: Dict[str, Any], 
        signature: str
    ) -> bool:
        """
        Verify a credential signature.

        Args:
            credential: The credential data
            signature: The signature to verify

        Returns:
            True if the signature is valid, False otherwise
        """
        return CryptoUtils.verify_signature(self.public_key, credential, signature)

    def get_public_key_path(self) -> str:
        """
        Get the path to the public key.

        Returns:
            Path to the public key file
        """
        return self.public_key_path
