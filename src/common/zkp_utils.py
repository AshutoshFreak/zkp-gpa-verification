#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Zero-Knowledge Proof utilities for the ZKP GPA verification system.

This module provides utilities for:
- Checking for required dependencies (snarkjs)
- Compiling circom circuits
- Generating and verifying zero-knowledge proofs
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List, Union


class ZKPUtils:
    """Utility class for Zero-Knowledge Proof operations."""

    @staticmethod
    def check_dependencies() -> Dict[str, bool]:
        """
        Check if required dependencies (snarkjs) are installed.

        Returns:
            Dictionary indicating if each dependency is installed
        """
        dependencies = {
            'snarkjs': False
        }
        
        # Check for snarkjs
        try:
            result = subprocess.run(
                ['snarkjs', '--version'], 
                capture_output=True, 
                text=True
            )
            # if result.returncode == 0:
            #     dependencies['snarkjs'] = True
            dependencies['snarkjs'] = True
        except FileNotFoundError:
            pass
            
        return dependencies

    @staticmethod
    def compile_circuit(
        circuit_path: str, 
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Compile a circom circuit.

        Args:
            circuit_path: Path to the circom circuit file
            output_dir: Directory where compiled circuit will be saved (default: same as circuit)

        Returns:
            Dictionary with paths to r1cs and wasm files
        """
        # Handle paths
        circuit_path = Path(circuit_path)
        if not output_dir:
            output_dir = circuit_path.parent
        else:
            output_dir = Path(output_dir)
            
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get circuit name without extension
        circuit_name = circuit_path.stem
        
        # Execute circom to compile the circuit
        cmd = [
            'circom', 
            str(circuit_path),
            '--r1cs', 
            '--wasm',
            '-o', 
            str(output_dir)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return {
                'r1cs': str(output_dir / f"{circuit_name}.r1cs"),
                'wasm': str(output_dir / f"{circuit_name}_js" / f"{circuit_name}.wasm")
            }
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to compile circuit: {e.stderr.decode()}")

    @staticmethod
    def setup_circuit(
        r1cs_path: str, 
        output_dir: Optional[str] = None,
        ptau_path: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Set up a circuit for zero-knowledge proofs.

        Args:
            r1cs_path: Path to the r1cs file
            output_dir: Directory where output files will be saved (default: same as r1cs)
            ptau_path: Path to the ptau file (default: download if not provided)

        Returns:
            Dictionary with paths to zkey and verification_key files
        """
        # Handle paths
        r1cs_path = Path(r1cs_path)
        if not output_dir:
            output_dir = r1cs_path.parent
        else:
            output_dir = Path(output_dir)
            
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get circuit name without extension
        circuit_name = r1cs_path.stem
        
        # If ptau_path is not provided, download a sample one for testing
        if not ptau_path:
            ptau_path = str(output_dir / "powersOfTau28_hez_final_08.ptau")
            if not Path(ptau_path).exists():
                print("Downloading Powers of Tau file...")
                subprocess.run([
                    'snarkjs', 
                    'powersoftau', 
                    'new', 
                    'bn128', 
                    '8', 
                    f"{ptau_path}.tmp"
                ], check=True)
                subprocess.run([
                    'snarkjs', 
                    'powersoftau', 
                    'prepare', 
                    'phase2', 
                    f"{ptau_path}.tmp", 
                    ptau_path
                ], check=True)
                os.remove(f"{ptau_path}.tmp")
        
        # Generate zkey
        zkey_path = str(output_dir / f"{circuit_name}.zkey")
        subprocess.run([
            'snarkjs', 
            'groth16', 
            'setup', 
            str(r1cs_path),
            ptau_path, 
            zkey_path
        ], check=True)
        
        # Export verification key
        vkey_path = str(output_dir / "verification_key.json")
        subprocess.run([
            'snarkjs', 
            'zkey', 
            'export', 
            'verificationkey', 
            zkey_path, 
            vkey_path
        ], check=True)
        
        return {
            'zkey': zkey_path,
            'verification_key': vkey_path
        }

    @staticmethod
    def generate_witness(
        wasm_path: str, 
        input_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> str:
        """
        Generate a witness for a circuit.

        Args:
            wasm_path: Path to the circuit WASM file
            input_data: Dictionary with input values for the circuit
            output_dir: Directory where the witness will be saved (default: same as wasm)

        Returns:
            Path to the generated witness file
        """
        # Handle paths
        wasm_path = Path(wasm_path)
        if not output_dir:
            # Go up one directory level from wasm_path/_js/
            output_dir = wasm_path.parent.parent
        else:
            output_dir = Path(output_dir)
            
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a temporary input file
        with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as tmp:
            json.dump(input_data, tmp)
            input_path = tmp.name
        
        # Generate witness
        witness_path = str(output_dir / "witness.wtns")
        try:
            # First go to the wasm directory
            wasm_dir = wasm_path.parent
            
            # Generate the witness
            cmd = f'cd {wasm_dir} && node generate_witness.js {wasm_path} {input_path} {witness_path}'
            subprocess.run(cmd, shell=True, check=True)
            
            return witness_path
        finally:
            # Remove temporary input file
            os.unlink(input_path)

    @staticmethod
    def generate_proof(
        zkey_path: str, 
        witness_path: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a zero-knowledge proof.

        Args:
            zkey_path: Path to the zkey file
            witness_path: Path to the witness file
            output_dir: Directory where proof files will be saved (default: same as witness)

        Returns:
            Dictionary with paths to proof and public input files
        """
        # Handle paths
        witness_path = Path(witness_path)
        if not output_dir:
            output_dir = witness_path.parent
        else:
            output_dir = Path(output_dir)
            
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate proof
        proof_path = str(output_dir / "proof.json")
        public_path = str(output_dir / "public.json")
        
        subprocess.run([
            'snarkjs', 
            'groth16', 
            'prove', 
            zkey_path, 
            witness_path, 
            proof_path, 
            public_path
        ], check=True)
        
        return {
            'proof': proof_path,
            'public': public_path
        }

    @staticmethod
    def verify_proof(
        verification_key_path: str, 
        proof_path: str, 
        public_path: str
    ) -> bool:
        """
        Verify a zero-knowledge proof.

        Args:
            verification_key_path: Path to the verification key file
            proof_path: Path to the proof file
            public_path: Path to the public input file

        Returns:
            True if the proof is valid, False otherwise
        """
        try:
            result = subprocess.run([
                'snarkjs', 
                'groth16', 
                'verify', 
                verification_key_path, 
                public_path, 
                proof_path
            ], capture_output=True, text=True, check=True)
            
            return "OK" in result.stdout
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def simplify_proof(
        proof_path: str, 
        public_path: str
    ) -> Dict[str, Any]:
        """
        Simplify a proof for transmission.

        Args:
            proof_path: Path to the proof file
            public_path: Path to the public input file

        Returns:
            Dictionary with simplified proof data
        """
        with open(proof_path, 'r') as f:
            proof = json.load(f)
            
        with open(public_path, 'r') as f:
            public = json.load(f)
            
        return {
            'proof': proof,
            'public': public
        }
