#!/usr/bin/env python3
"""
npm_batch_installer.py

Reads tampered_package_names.txt (one npm package per line, e.g. lodash@4.17.21 or @scope/pkg@1.2.3)
and attempts to 'install' each package in an isolated temporary directory using:
  npm install <pkg> --ignore-scripts --no-audit --no-fund

This avoids running package lifecycle scripts and reduces side effects.
Always run inside an isolated environment (container/VM) when working with untrusted packages.
"""

import subprocess
import shutil
import sys
import tempfile
from pathlib import Path

TAMPERED_FILE = "tampered_package_names.txt"

def run_cmd(cmd, cwd=None):
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return (True, proc.stdout, proc.stderr)
    except subprocess.CalledProcessError as e:
        return (False, e.stdout, e.stderr)

def install_and_verify(package_name):
    print(f"\nInstalling: {package_name}")

    # Create isolated temporary directory for this install
    with tempfile.TemporaryDirectory(prefix="npm_install_") as td:
        td_path = Path(td)

        # initialize a minimal package.json so npm will install into node_modules here
        ok, out, err = run_cmd(["npm", "init", "-y"], cwd=td)
        if not ok:
            print(f"❌ npm init failed for {package_name}\n{err}")
            return False

        # install package but do NOT run lifecycle scripts; disable audit/fund to reduce network chatter
        install_cmd = [
            "npm", "install", package_name,
            "--ignore-scripts",
            "--no-audit",
            "--no-fund",
            "--silent"
        ]
        ok, out, err = run_cmd(install_cmd, cwd=td)
        if not ok:
            print(f"❌ Failed to install: {package_name}")
            print(f"Error:\n{err.strip() or out.strip()}")
            return False

        # Simple verification: check `npm ls <pkg> --depth=0` exit code (succeeds when installed)
        # Use --silent to minimize noisy output. We run it in the same temp dir.
        verify_cmd = ["npm", "ls", package_name, "--depth=0", "--silent"]
        ok, out, err = run_cmd(verify_cmd, cwd=td)
        if ok:
            # optionally, we can check that node_modules/<pkg> exists
            # compute path (for scoped packages, pkg path includes the scope directory)
            node_modules = td_path / "node_modules"
            # For verification, just report success and discard tempdir (no persistence)
            print(f"✅ Successfully installed (verified): {package_name}")
            return True
        else:
            print(f"❌ Verification failed for: {package_name}")
            print(f"npm ls output / error:\n{err.strip() or out.strip()}")
            return False

def main():
    try:
        with open(TAMPERED_FILE, "r", encoding="utf-8") as f:
            packages = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
    except FileNotFoundError:
        print(f"File not found: {TAMPERED_FILE}")
        sys.exit(2)

    success, failure = [], []

    for pkg in packages:
        if install_and_verify(pkg):
            success.append(pkg)
        else:
            failure.append(pkg)

    print("\n=== Summary ===")
    print(f"✅ Installed: {success}")
    print(f"❌ Failed: {failure}")

if __name__ == "__main__":
    # quick check: ensure npm is available
    if shutil.which("npm") is None:
        print("ERROR: npm is not found in PATH. Install Node.js/npm or run inside an environment with npm available.")
        sys.exit(1)
    main()
