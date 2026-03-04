import os
import subprocess

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
script_path = os.path.join(base_dir, "scripts", "process_pipeline.py")

if not os.path.exists(data_dir):
    print("No data directory found.")
    exit(1)

files = sorted(os.listdir(data_dir))

# First run on demo files to create v1
demo_files = [f for f in files if f.startswith("demo_")]
for df in demo_files:
    print(f"Running pipeline on {df}...")
    subprocess.run(["python", script_path, os.path.join(data_dir, df)])

# Then run on onboarding files to create v2
onboarding_files = [f for f in files if f.startswith("onboarding_")]
for of in onboarding_files:
    print(f"Running pipeline on {of}...")
    subprocess.run(["python", script_path, os.path.join(data_dir, of)])

print("Batch processing complete.")
