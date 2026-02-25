#!/usr/bin/env python3
import subprocess
import os
import sys
from datetime import datetime

def run_command(command, description):
    print(f"\n>>> Starting: {description}")
    print(f"Executing: {command}")
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in process.stdout:
            print(line, end='')
            sys.stdout.flush()
        process.wait()
        if process.returncode == 0:
            print(f"--- SUCCESS: {description}")
            return True
        else:
            print(f"--- FAILED: {description} (Exit Code: {process.returncode})")
            return False
    except Exception as e:
        print(f"--- ERROR: {description} -> {e}")
        return False

def main():
    start_time = datetime.now()
    print("="*60)
    print(f"🚀 LOCAL MARKET SYNC START: {start_time}")
    print("="*60)

    # 1. Pull latest changes
    if not run_command("git pull origin main", "Pulling latest changes from GitHub"):
        print("Warning: git pull failed. Continuing anyway...")

    # 2. Run KAP Monitor
    run_command(f"{sys.executable} kap_monitor.py --once", "Running KAP Monitor Snapshot")

    # 3. Run BIST Scanner (Turbo Mode)
    # Ensure GITHUB_ACTIONS is NOT set so it uses full power if configured
    run_command(f"{sys.executable} bist_scanner.py", "Running BIST Market Scanner (Turbo)")

    # 4. Run US Scanner (Turbo Mode)
    run_command(f"{sys.executable} us_scanner.py", "Running US Market Scanner (Turbo)")

    # 5. Commit and Push
    commit_msg = f"Data Auto-Update (Local): {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    # Use git commit -a and check if anything changed to avoid exit code 1
    git_chain = f'git add . && git commit -m "{commit_msg}" || echo "No changes to commit" && git push origin main'
    run_command(git_chain, "Committing and Pushing Updates to GitHub")

    end_time = datetime.now()
    duration = end_time - start_time
    print("\n" + "="*60)
    print(f"🏆 LOCAL MARKET SYNC COMPLETE!")
    print(f"Started:  {start_time}")
    print(f"Finished: {end_time}")
    print(f"Duration: {duration}")
    print("="*60)
    print("Vercel deployment will start automatically on GitHub push. Check your site in a few minutes!")

if __name__ == "__main__":
    main()
