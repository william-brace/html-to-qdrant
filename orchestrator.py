import subprocess
import os
import time
from typing import List
import sys
import argparse

# Define all available states
ALL_STATES = ["ny", "nj", "or", "co", "ct", "ca", "ma", "wa", "ri", "dc", "general"]

def parse_args():
    parser = argparse.ArgumentParser(
        description='Process PFL data pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python orchestrator.py --states ny --collection-name "{state}-pfl-2025"
  python orchestrator.py --states ny ca wa --collection-name "{state}-chunk-links"
  python orchestrator.py --all --collection-name "{state}-pfl-data" --overwrite
        '''
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--states', nargs='+', choices=ALL_STATES,
                      help='List of state codes to process (e.g., ny ca wa)')
    group.add_argument('--all', action='store_true',
                      help='Process all available states')
    parser.add_argument('--overwrite', action='store_true',
                      help='Overwrite existing vector collections')
    parser.add_argument('--collection-name', required=True, type=str,
                      help='Collection name format with {state} placeholder (e.g., "{state}-pfl-2025")')
    return parser.parse_args()

def run_script(script_name: str, description: str, states: List[str] = None, overwrite: bool = False, collection_name: str = None) -> bool:
    """
    Run a Python script and handle its execution.
    Returns True if successful, False otherwise.
    """
    print(f"\n{'='*80}")
    print(f"Starting: {description}")
    print(f"{'='*80}\n")
    
    try:
        cmd = [sys.executable, script_name]
        if states:
            cmd.extend(['--states'] + states)
        if overwrite and script_name == "vectorizor.py":
            cmd.append('--overwrite')
        if collection_name:
            cmd.extend(['--collection-name', collection_name])
        
        result = subprocess.run(cmd, check=True)
        if result.returncode == 0:
            print(f"\n✅ Successfully completed: {description}")
            return True
        else:
            print(f"\n❌ Failed: {description}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error running {script_name}: {str(e)}")
        return False

def check_required_files(files: List[str]) -> bool:
    """
    Check if all required script files exist.
    """
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print("❌ Error: The following required files are missing:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    return True

def main():
    args = parse_args()
    
    # Validate collection name format
    if '{state}' not in args.collection_name:
        print("❌ Error: Collection name must contain {state} placeholder")
        return
    
    # Define the scripts to run in order
    scripts = [
        ("getHTML.py", "Scraping HTML files from websites"),
        ("cleaner.py", "Cleaning HTML files and converting to text"),
        ("chunker-new.py", "Chunking text files into smaller segments"),
        ("vectorizor.py", "Vectorizing chunks and storing in vector database")
    ]
    
    # Get states to process
    states_to_process = ALL_STATES if args.all else args.states
    
    # Check if all required scripts exist
    if not check_required_files([script[0] for script in scripts]):
        return
    
    # Record start time
    start_time = time.time()
    
    # Run each script in sequence
    for script_name, description in scripts:
        if not run_script(script_name, description, states_to_process, args.overwrite, args.collection_name):
            print("\n❌ Pipeline failed. Stopping execution.")
            return
        
        # Add a small delay between scripts
        time.sleep(2)
    
    # Calculate total execution time
    execution_time = time.time() - start_time
    
    print("\n" + "="*80)
    print("🎉 Pipeline completed successfully!")
    print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
    print("="*80)

if __name__ == "__main__":
    main() 