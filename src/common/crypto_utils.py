#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cryptographic utilities for the ZKP GPA verification system.

This module provides cryptographic functions for:
- Key generation
- Signing credentials
- Verifying signatures
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


class CryptoUtils:
    """Utility class for cryptographic operations."""

    @staticmethod
    def generate_key_pair(
        key_size: int = 2048
    ) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """
        Generate an RSA key pair.

        Args:
            key_size: The size of the key in bits (default: 2048)

        Returns:
            A tuple containing (private_key, public_key)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def save_private_key(
        private_key: rsa.RSAPrivateKey, 
        path: str, 
        password: Optional[str] = None
    ) -> None:
        """
        Save a private key to a file, optionally encrypted with a password.

        Args:
            private_key: The private key to save
            path: Path where the key will be saved
            password: Optional password for encryption (default: None)

        Returns:
            None
        """
        # Create directory if it doesn't exist
        key_path = Path(path)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Serialize key with password if provided
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(
                password.encode()
            )
        else:
            encryption_algorithm = serialization.NoEncryption()
            
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )
        
        with open(key_path, 'wb') as f:
            f.write(pem)

    @staticmethod
    def save_public_key(public_key: rsa.RSAPublicKey, path: str) -> None:
        """
        Save a public key to a file.

        Args:
            public_key: The public key to save
            path: Path where the key will be saved

        Returns:
            None
        """
        # Create directory if it doesn't exist
        key_path = Path(path)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        
        with open(key_path, 'wb') as f:
            f.write(pem)

    @staticmethod
    def load_private_key(
        path: str, 
        password: Optional[str] = None
    ) -> rsa.RSAPrivateKey:
        """
        Load a private key from a file.

        Args:
            path: Path to the private key file
            password: Optional password for decryption (default: None)

        Returns:
            The loaded private key
        """
        with open(path, 'rb') as f:
            private_key_pem = f.read()
            
        if password:
            return serialization.load_pem_private_key(
                private_key_pem,
                password=password.encode()
            )
        
        return serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )

    @staticmethod
    def load_public_key(path: str) -> rsa.RSAPublicKey:
        """
        Load a public key from a file.

        Args:
            path: Path to the public key file

        Returns:
            The loaded public key
        """
        with open(path, 'rb') as f:
            public_key_pem = f.read()
            
        return serialization.load_pem_public_key(public_key_pem)

    @staticmethod
    def sign_data(
        private_key: rsa.RSAPrivateKey, 
        data: Dict[str, Any]
    ) -> str:
        """
        Sign a dictionary of data.

        Args:
            private_key: The private key to use for signing
            data: Dictionary of data to sign

        Returns:
            Base64-encoded signature
        """
        # Serialize the data to a consistent format for signing
        data_bytes = json.dumps(data, sort_keys=True).encode()
        
        signature = private_key.sign(
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode()

    @staticmethod
    def verify_signature(
        public_key: rsa.RSAPublicKey, 
        data: Dict[str, Any], 
        signature: str
    ) -> bool:
        """
        Verify the signature of a data dictionary.

        Args:
            public_key: The public key to use for verification
            data: Dictionary of data that was signed
            signature: Base64-encoded signature to verify

        Returns:
            True if signature is valid, False otherwise
        """
        data_bytes = json.dumps(data, sort_keys=True).encode()
        signature_bytes = base64.b64decode(signature)
        
        try:
            public_key.verify(
                signature_bytes,
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False
