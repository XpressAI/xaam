#!/usr/bin/env python3
"""
Script to run Alembic migrations
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

def run_migrations(revision=None, downgrade=False, autogenerate=False, message=None):
    """
    Run Alembic migrations
    
    Args:
        revision: Revision to upgrade/downgrade to
        downgrade: Whether to downgrade
        autogenerate: Whether to autogenerate a migration
        message: Message for the migration
    """
    # Change to the backend directory
    os.chdir(ROOT_DIR)
    
    # Build the command
    cmd = ["alembic"]
    
    if downgrade:
        cmd.extend(["downgrade", revision or "base"])
    elif autogenerate:
        if not message:
            print("Error: Message is required for autogenerate")
            sys.exit(1)
        cmd.extend(["revision", "--autogenerate", "-m", message])
    elif revision:
        cmd.extend(["upgrade", revision])
    else:
        cmd.extend(["upgrade", "head"])
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Print the output
    print(result.stdout)
    
    if result.stderr:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    print("Migrations completed successfully")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Alembic migrations")
    parser.add_argument("--revision", help="Revision to upgrade/downgrade to")
    parser.add_argument("--downgrade", action="store_true", help="Downgrade instead of upgrade")
    parser.add_argument("--autogenerate", action="store_true", help="Autogenerate a migration")
    parser.add_argument("--message", help="Message for the migration")
    
    args = parser.parse_args()
    
    run_migrations(
        revision=args.revision,
        downgrade=args.downgrade,
        autogenerate=args.autogenerate,
        message=args.message
    )