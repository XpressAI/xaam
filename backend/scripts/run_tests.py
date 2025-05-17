#!/usr/bin/env python3
"""
Script to run tests
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

def run_tests(test_path=None, unit=False, integration=False, api=False, coverage=False):
    """
    Run tests
    
    Args:
        test_path: Path to specific test file or directory
        unit: Whether to run unit tests
        integration: Whether to run integration tests
        api: Whether to run API tests
        coverage: Whether to generate coverage report
    """
    # Change to the backend directory
    os.chdir(ROOT_DIR)
    
    # Build the command
    cmd = ["pytest", "-v"]
    
    # Add markers
    markers = []
    if unit:
        markers.append("unit")
    if integration:
        markers.append("integration")
    if api:
        markers.append("api")
    
    if markers:
        cmd.append("-m")
        cmd.append(" or ".join(markers))
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # Add test path
    if test_path:
        cmd.append(test_path)
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    # Return the exit code
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests")
    parser.add_argument("--path", help="Path to specific test file or directory")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    args = parser.parse_args()
    
    # If no test type is specified, run all tests
    if not (args.unit or args.integration or args.api):
        args.unit = True
        args.integration = True
        args.api = True
    
    exit_code = run_tests(
        test_path=args.path,
        unit=args.unit,
        integration=args.integration,
        api=args.api,
        coverage=args.coverage
    )
    
    sys.exit(exit_code)