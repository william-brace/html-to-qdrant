import subprocess
import os
import time
from typing import List
import sys

def run_script(script_name: str, description: str, states: List[str] = None, overwrite: bool = False) -> bool:
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
    # Define the scripts to run in order
    scripts = [
        ("getHTML.py", "Scraping HTML files from websites"),
        ("cleaner.py", "Cleaning HTML files and converting to text"),
        ("chunker-new.py", "Chunking text files into smaller segments"),
        ("vectorizor.py", "Vectorizing chunks and storing in vector database")
    ]
    
    # Optional: Define specific states to process (comment out to use defaults)
    states_to_process = ["or"]  # Example states
    overwrite_vectors = True  # Set to True to overwrite existing collections
    
    # Check if all required scripts exist
    if not check_required_files([script[0] for script in scripts]):
        return
    
    # Record start time
    start_time = time.time()
    
    # Run each script in sequence
    for script_name, description in scripts:
        if not run_script(script_name, description, states_to_process, overwrite_vectors):
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