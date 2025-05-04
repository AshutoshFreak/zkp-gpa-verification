#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive demonstration for the ZKP GPA verification system.

This module provides an interactive CLI for demonstrating how different
parties interact with the system during a presentation.
"""

import os
import json
import logging
import argparse
import time
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

# Import components
from .credential_db.database import CredentialDatabase
from .signing_org.credential_issuer import CredentialIssuer
from .student.credential_holder import CredentialHolder
from .institution.verifier import ProofVerifier
from .common.zkp_utils import ZKPUtils


# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_role(role):
    """Print the current role."""
    if role == "student":
        color = Colors.BLUE
    elif role == "school":
        color = Colors.GREEN
    elif role == "university":
        color = Colors.YELLOW
    else:
        color = Colors.CYAN
        
    print(f"\n{color}{Colors.BOLD}[{role.upper()}]{Colors.ENDC}\n")


def print_step(text):
    """Print a step in the process."""
    print(f"{Colors.CYAN}➤ {text}{Colors.ENDC}")


def print_info(text):
    """Print information text."""
    print(f"  {Colors.GREEN}✓ {text}{Colors.ENDC}")


def print_error(text):
    """Print error text."""
    print(f"  {Colors.RED}✗ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning text."""
    print(f"  {Colors.YELLOW}⚠ {text}{Colors.ENDC}")


def input_with_prompt(prompt):
    """Get input with a formatted prompt."""
    return input(f"{Colors.BOLD}{prompt}: {Colors.ENDC}")


def press_enter():
    """Prompt the user to press Enter to continue."""
    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")


def typewriter_print(text, delay=0.03):
    """Print text with a typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


class InteractiveDemo:
    """Interactive demonstration of the ZKP GPA verification system."""

    def __init__(self):
        """Initialize the interactive demo."""
        # Set up core components
        self.db = CredentialDatabase()
        self.issuer = None
        self.student = None
        self.university = None
        
        # Demo state
        self.student_id = "student123"
        self.student_name = "Alex Johnson"
        self.score_type = "gpa"
        self.score_value = 3.8
        self.threshold = 3.5
        self.credential = None
        self.proof_data = None
        
        # Set up script directory for the circuit path
        self.script_dir = Path(__file__).parent.parent
        self.circuit_path = str(self.script_dir / "circuits" / "threshold_check.circom")
        
        # Check dependencies
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        dependencies = ZKPUtils.check_dependencies()
        if not dependencies["snarkjs"]:
            print_error("Missing dependency: snarkjs not installed")
            print_info("Please install snarkjs with: npm install -g snarkjs")
            sys.exit(1)
            
        # # Check for circomlib
        # circuit_dir = Path(self.circuit_path).parent
        # node_modules = circuit_dir / "node_modules"
        # circomlib = node_modules / "circomlib"
        # if not circomlib.exists():
        #     print_error("circomlib not found in node_modules directory")
        #     print_info("Please run the initialization script: ./init_circuit_deps.sh")
        #     sys.exit(1)

    def run(self):
        """Run the interactive demo."""
        clear_screen()
        self._show_welcome()
        
        while True:
            self._show_main_menu()
            choice = input_with_prompt("Choose an option (1-5)")
            
            if choice == '1':
                self._setup_demo()
            elif choice == '2':
                self._run_student_flow()
            elif choice == '3':
                self._run_school_flow()
            elif choice == '4':
                self._run_university_flow()
            elif choice == '5':
                print_info("Thank you for using the ZKP GPA Verification Demo!")
                break
            else:
                print_error("Invalid choice. Please try again.")
                press_enter()

    def _show_welcome(self):
        """Show the welcome screen."""
        print_header("ZKP GPA Verification System")
        
        welcome_text = [
            f"{Colors.BOLD}Welcome to the Zero-Knowledge Proof GPA Verification System!{Colors.ENDC}",
            "",
            "This interactive demo showcases how students can prove their",
            "academic qualifications without revealing their actual scores.",
            "",
            "The system involves three main parties:",
            f"  {Colors.BLUE}• Student{Colors.ENDC} - Holds credentials and generates proofs",
            f"  {Colors.GREEN}• School/Issuer{Colors.ENDC} - Issues signed credentials",
            f"  {Colors.YELLOW}• University{Colors.ENDC} - Verifies proofs without seeing scores"
        ]
        
        for line in welcome_text:
            typewriter_print(line, 0.01)
            
        press_enter()

    def _show_main_menu(self):
        """Show the main menu."""
        clear_screen()
        print_header("Main Menu")
        
        print(f"1. {Colors.CYAN}Setup Demo{Colors.ENDC} - Initialize the system and create test data")
        print(f"2. {Colors.BLUE}Student Flow{Colors.ENDC} - Request credential and generate proof")
        print(f"3. {Colors.GREEN}School Flow{Colors.ENDC} - Issue credentials to students")
        print(f"4. {Colors.YELLOW}University Flow{Colors.ENDC} - Verify student proofs")
        print(f"5. {Colors.RED}Exit{Colors.ENDC}")
        print()

    def _setup_demo(self):
        """Set up the demo environment."""
        clear_screen()
        print_header("Setting Up Demo Environment")
        print_role("system")
        
        print_step("Creating test database with student records...")
        self.db = CredentialDatabase()
        
        # Ask for student details
        print("\nLet's set up a test student:")
        self.student_id = input_with_prompt("Student ID (default: student123)") or "student123"
        self.student_name = input_with_prompt("Student Name (default: Alex Johnson)") or "Alex Johnson"
        self.score_type = input_with_prompt("Score Type (default: gpa)") or "gpa"
        try:
            score_input = input_with_prompt(f"{self.score_type.upper()} Value (default: 3.8)") or "3.8"
            self.score_value = float(score_input)
        except ValueError:
            print_error("Invalid score value, using default of 3.8")
            self.score_value = 3.8
            
        try:
            threshold_input = input_with_prompt(f"Threshold Value (default: 3.5)") or "3.5"
            self.threshold = float(threshold_input)
        except ValueError:
            print_error("Invalid threshold value, using default of 3.5")
            self.threshold = 3.5
        
        # Add student to database
        if self.db.has_student(self.student_id):
            self.db.update_student_scores(self.student_id, {self.score_type: self.score_value})
            print_info(f"Updated {self.student_name}'s {self.score_type.upper()} to {self.score_value}")
        else:
            self.db.add_student(self.student_id, {self.score_type: self.score_value})
            print_info(f"Added student {self.student_name} with {self.score_type.upper()} of {self.score_value}")
        
        print_step("Setting up credential issuer (school)...")
        self.issuer = CredentialIssuer("ExampleSchool", credential_db=self.db)
        print_info("School credential issuer initialized")
        print_info(f"Public key path: {self.issuer.get_public_key_path()}")
        
        print_step("Setting up student credential holder...")
        self.student = CredentialHolder(self.student_id)
        print_info(f"Student credential holder for {self.student_name} initialized")
        
        print_step("Setting up university verifier...")
        self.university = ProofVerifier("ExampleUniversity")
        self.university.add_trusted_issuer("ExampleSchool", self.issuer.get_public_key_path())
        print_info("University verifier initialized")
        print_info("Added school as a trusted issuer")
        
        print_info(f"\nDemo setup complete! The system is ready to demonstrate:")
        print_info(f"- Student: {self.student_name} (ID: {self.student_id})")
        print_info(f"- {self.score_type.upper()}: {self.score_value}")
        print_info(f"- Threshold: {self.threshold}")
        
        press_enter()

    def _run_student_flow(self):
        """Run the student flow of the demo."""
        clear_screen()
        print_header("Student Flow")
        print_role("student")
        
        if not self.student:
            print_error("Student not initialized. Please run Setup Demo first.")
            press_enter()
            return
            
        print_step(f"Student {self.student_name} needs to apply to universities")
        print_info(f"Need to prove {self.score_type.upper()} meets university requirements")
        print_info(f"The university requires {self.score_type.upper()} >= {self.threshold}")
        press_enter()
        
        print_step("Requesting credential from school...")
        if not self.credential:
            self.credential = self.issuer.issue_credential(self.student_id, self.score_type)
            if not self.credential:
                print_error(f"Failed to get credential from school")
                press_enter()
                return
                
            print_info(f"Received signed credential for {self.score_type.upper()}")
            self.student.store_credential(self.credential)
            print(sys.getsizeof(self.credential))
            print_info("Credential stored securely")
        else:
            print_info("Already have a credential from school")
        
        press_enter()
        
        print_step("Generating zero-knowledge proof...")
        print_info(f"Proving that: {self.score_type.upper()} >= {self.threshold}")
        print_info(f"WITHOUT revealing that {self.score_type.upper()} = {self.score_value}")
        
        credential_id = self.credential["credential"]["credential_id"]
        self.proof_data = self.student.generate_proof(credential_id, self.threshold, self.circuit_path)
        
        if not self.proof_data:
            print_error("Failed to generate proof")
            press_enter()
            return
            
        print_info("Zero-knowledge proof generated successfully!")
        print_info("Proof contains cryptographic evidence that the score meets the threshold")
        print_info("The actual score remains private and is not disclosed to the university")
        
        press_enter()

        print_step("Sending proof to university...")
        print_info("Proof sent to university admission system")
        print_info("Waiting for verification result...")
        
        press_enter()

    def _run_school_flow(self):
        """Run the school/issuer flow of the demo."""
        clear_screen()
        print_header("School/Issuer Flow")
        print_role("school")
        
        if not self.issuer:
            print_error("School not initialized. Please run Setup Demo first.")
            press_enter()
            return
            
        print_step("School receives credential request from student")
        print_info(f"Student: {self.student_name} (ID: {self.student_id})")
        print_info(f"Requesting credential for: {self.score_type.upper()}")
        
        press_enter()
        
        print_step("Retrieving student records from database...")
        scores = self.db.get_student_scores(self.student_id)
        if not scores:
            print_error(f"No records found for student {self.student_id}")
            press_enter()
            return
            
        print_info(f"Found student record: {self.score_type.upper()} = {scores[self.score_type]}")
        
        press_enter()
        
        print_step("Issuing signed credential...")
        self.credential = self.issuer.issue_credential(self.student_id, self.score_type)
        if not self.credential:
            print_error(f"Failed to issue credential")
            press_enter()
            return
            
        print_info(f"Created credential with unique ID: {self.credential['credential']['credential_id']}")
        print_info(f"Credential contains {self.score_type.upper()} value: {self.score_value}")
        print_info("Credential signed with school's private key")
        
        press_enter()
        
        print_step("Sending credential to student...")
        print_info(f"Credential for {self.score_type.upper()} sent to {self.student_name}")
        
        press_enter()
        
        print_step("Waiting for verification requests from universities...")
        print_info("The school will verify the authenticity of credentials when requested")
        
        press_enter()

    def _run_university_flow(self):
        """Run the university flow of the demo."""
        clear_screen()
        print_header("University Flow")
        print_role("university")
        
        if not self.university:
            print_error("University not initialized. Please run Setup Demo first.")
            press_enter()
            return
            
        if not self.proof_data:
            print_error("No proof received from student. Please run Student Flow first.")
            press_enter()
            return
            
        print_step("University receives application from student")
        print_info(f"Student: {self.student_name} (ID: {self.student_id})")
        print_info(f"Application includes a zero-knowledge proof for {self.score_type.upper()}")
        print_info(f"University requirement: {self.score_type.upper()} >= {self.threshold}")
        
        press_enter()
        
        print_step("Verifying the zero-knowledge proof...")
        student_proof_dir = Path.home() / ".zkp_gpa_verification" / "students" / self.student_id / "proofs"
        credential_id = self.proof_data["metadata"]["credential_id"]
        verification_key_path = str(student_proof_dir / credential_id / "verification_key.json")
        
        verification_result = self.university.verify_proof(
            self.proof_data, 
            verification_key_path, 
            self.threshold
        )
        
        if not verification_result["valid"]:
            print_error(f"Proof verification failed: {verification_result.get('error', 'Unknown error')}")
            press_enter()
            return
            
        print_info("Proof verification successful!")
        print_info(f"Confirmed: Student's {self.score_type.upper()} meets the threshold of {self.threshold}")
        print_info("The university does NOT know the actual score value")
        
        press_enter()
        
        print_step("Verifying credential with issuing school...")
        issuer_verification = self.university.verify_with_issuer(self.proof_data, self.issuer)
        
        if not issuer_verification["valid"]:
            print_error(f"Issuer verification failed: {issuer_verification.get('error', 'Unknown error')}")
            press_enter()
            return
            
        print_info("Issuer verification successful!")
        print_info("School confirmed the credential is authentic")
        
        press_enter()
        
        print_step("Making admission decision...")
        print_info(f"Student {self.student_name} meets the {self.score_type.upper()} requirement")
        print_info("The admission process can continue based on this verification")
        print_info("At no point was the actual score value revealed to the university")
        
        press_enter()


def main():
    """Main function to run the interactive demo."""
    parser = argparse.ArgumentParser(description='ZKP GPA Verification Interactive Demo')
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the interactive demo
    demo = InteractiveDemo()
    demo.run()


if __name__ == "__main__":
    main()
