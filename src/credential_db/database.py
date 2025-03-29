#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Credential database module for the ZKP GPA verification system.

This module simulates a database that stores student academic records.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List


class CredentialDatabase:
    """Simulates a database of student credentials and scores."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the credential database.

        Args:
            db_path: Path to the JSON file storing the database (default: creates a new one)
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            # Default path in user's home directory
            self.db_path = Path.home() / ".zkp_gpa_verification" / "credential_db.json"
            
        # Create directory if it doesn't exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize or load the database
        if not self.db_path.exists():
            self._db = {
                "students": {}
            }
            self._save()
        else:
            self._load()

    def _load(self) -> None:
        """
        Load the database from file.
        
        Returns:
            None
        """
        try:
            with open(self.db_path, 'r') as f:
                self._db = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Error loading database: {e}")
            self._db = {"students": {}}
            self._save()

    def _save(self) -> None:
        """
        Save the database to file.
        
        Returns:
            None
        """
        with open(self.db_path, 'w') as f:
            json.dump(self._db, f, indent=2)

    def add_student(
        self, 
        student_id: str, 
        scores: Dict[str, float]
    ) -> bool:
        """
        Add a student and their scores to the database.

        Args:
            student_id: Unique identifier for the student
            scores: Dictionary of score types and values (e.g., {"gpa": 3.8, "sat": 1450})

        Returns:
            True if the student was added successfully, False otherwise
        """
        if student_id in self._db["students"]:
            logging.warning(f"Student {student_id} already exists in database")
            return False
            
        self._db["students"][student_id] = {
            "scores": scores
        }
        self._save()
        return True

    def update_student_scores(
        self, 
        student_id: str, 
        scores: Dict[str, float]
    ) -> bool:
        """
        Update a student's scores in the database.

        Args:
            student_id: Unique identifier for the student
            scores: Dictionary of score types and values to update

        Returns:
            True if the scores were updated successfully, False otherwise
        """
        if student_id not in self._db["students"]:
            logging.warning(f"Student {student_id} does not exist in database")
            return False
            
        # Update the scores
        current_scores = self._db["students"][student_id]["scores"]
        current_scores.update(scores)
        self._save()
        return True

    def get_student_scores(self, student_id: str) -> Optional[Dict[str, float]]:
        """
        Get a student's scores from the database.

        Args:
            student_id: Unique identifier for the student

        Returns:
            Dictionary of score types and values, or None if student not found
        """
        if student_id not in self._db["students"]:
            logging.warning(f"Student {student_id} does not exist in database")
            return None
            
        return self._db["students"][student_id]["scores"]

    def delete_student(self, student_id: str) -> bool:
        """
        Delete a student from the database.

        Args:
            student_id: Unique identifier for the student

        Returns:
            True if the student was deleted successfully, False otherwise
        """
        if student_id not in self._db["students"]:
            logging.warning(f"Student {student_id} does not exist in database")
            return False
            
        del self._db["students"][student_id]
        self._save()
        return True

    def list_students(self) -> List[str]:
        """
        List all student IDs in the database.

        Returns:
            List of student IDs
        """
        return list(self._db["students"].keys())

    def has_student(self, student_id: str) -> bool:
        """
        Check if a student exists in the database.

        Args:
            student_id: Unique identifier for the student

        Returns:
            True if the student exists, False otherwise
        """
        return student_id in self._db["students"]
