"""
Run all data creator scripts in sequence.
This script executes all data generation scripts in the data_creators folder.
"""
import subprocess
import sys
from pathlib import Path

# Define scripts to run in order
SCRIPTS = [
    'create_base.py',
    'create_base_all_metrics.py',
    'create_base_extracted_features.py',
    'create_base_extracted_all_metrics.py',
    'create_base_relative_features.py',
    'create_base_user_specific.py',
]

def run_script(script_name):
    """Run a single script and handle its output."""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"⚠️  Warning: {script_name} not found, skipping...")
        return False
    
    print(f"\n{'='*80}")
    print(f"Running: {script_name}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            check=True,
            capture_output=False
        )
        print(f"\n✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {script_name} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n✗ {script_name} failed with error: {e}")
        return False

def main():
    """Run all scripts in sequence."""
    print("Starting data creators batch execution...")
    print(f"Total scripts to run: {len(SCRIPTS)}")
    
    results = {}
    for script in SCRIPTS:
        success = run_script(script)
        results[script] = success
        
        if not success:
            print(f"\n⚠️  Warning: {script} failed, but continuing with remaining scripts...")
    
    # Print summary
    print(f"\n{'='*80}")
    print("EXECUTION SUMMARY")
    print(f"{'='*80}")
    
    successful = sum(1 for v in results.values() if v)
    failed = len(results) - successful
    
    for script, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {script}")
    
    print(f"\nTotal: {successful} successful, {failed} failed out of {len(results)} scripts")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("\n🎉 All scripts completed successfully!")

if __name__ == "__main__":
    main()
