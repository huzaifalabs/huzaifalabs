#!/usr/bin/env python3
"""
Orchestrator: fetch data, generate SVG assets, build README.

Usage:
    python scripts/update_profile.py           # full pipeline
    python scripts/update_profile.py --skip-fetch  # use cached data

Environment:
    GITHUB_TOKEN  (optional, but recommended for higher rate limits)
"""

import os
import subprocess
import sys


def run(script: str, args: list[str] = []) -> bool:
    """Run a script and return success status."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base, "scripts", script)
    cmd = [sys.executable, script_path] + args
    print(f"\n{'='*50}")
    print(f"  Running: {script}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=base)
    if result.returncode != 0:
        print(f"  FAILED: {script} exited with code {result.returncode}")
        return False
    return True


def main():
    skip_fetch = "--skip-fetch" in sys.argv

    if not skip_fetch:
        if not run("fetch_data.py"):
            print("\n[!] Data fetch failed. Attempting to use cached data...")
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(os.path.join(base, "data", "github_data.json")):
                print("[!] No cached data available. Aborting.")
                sys.exit(1)
            print("[+] Using cached data from previous run.")

    if not run("generate_assets.py"):
        print("\n[!] Asset generation failed.")
        sys.exit(1)

    if not run("build_readme.py"):
        print("\n[!] README generation failed.")
        sys.exit(1)

    print("\n" + "="*50)
    print("  Profile update complete!")
    print("="*50)


if __name__ == "__main__":
    main()
