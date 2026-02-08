#!/usr/bin/env python3
"""
CLI wrapper for ops-snapshot-audit.
"""

import argparse
import subprocess
import sys
import os
import zipfile
import shutil
from datetime import datetime


def run_ansible(inventory, profile):
    """Execute ansible-playbook with given inventory and profile."""
    cmd = [
        "ansible-playbook",
        "-i", inventory,
        "playbooks/snapshot.yml",
        "-e", f"profile_file={profile}"
    ]
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print("Ansible playbook failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def zip_output(output_dir="output", zip_name=None):
    """Package the output directory into a zip file."""
    if not zip_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"snapshot_audit_{timestamp}.zip"
    
    if not os.path.exists(output_dir):
        print(f"Output directory '{output_dir}' not found.")
        return None
    
    zip_path = os.path.join(os.path.dirname(output_dir), zip_name)
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_dir)
                zipf.write(file_path, arcname)
    print(f"Created zip archive: {zip_path}")
    return zip_path


def main():
    parser = argparse.ArgumentParser(
        description="Ops Snapshot Audit - Agentless read-only Linux audit via SSH"
    )
    parser.add_argument(
        "-i", "--inventory",
        default="inventories/example.yml",
        help="Path to Ansible inventory file"
    )
    parser.add_argument(
        "-p", "--profile",
        default="profiles/mipro-linux.yml",
        help="Path to audit profile YAML"
    )
    parser.add_argument(
        "-z", "--zip",
        action="store_true",
        help="Package output into a zip file after audit"
    )
    parser.add_argument(
        "--zip-name",
        help="Custom name for the zip file"
    )
    
    args = parser.parse_args()
    
    # Validate files exist
    if not os.path.exists(args.inventory):
        print(f"Inventory file not found: {args.inventory}")
        sys.exit(1)
    if not os.path.exists(args.profile):
        print(f"Profile file not found: {args.profile}")
        sys.exit(1)
    
    # Run ansible playbook
    success = run_ansible(args.inventory, args.profile)
    if not success:
        sys.exit(1)
    
    # Zip output if requested
    if args.zip or args.zip_name:
        zip_path = zip_output("output", args.zip_name)
        if not zip_path:
            sys.exit(1)
    
    print("Audit completed successfully.")


if __name__ == "__main__":
    main()