import os
import subprocess
import sys
import time
import requests

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data")
script_path = os.path.join(base_dir, "scripts", "process_pipeline.py")

if not os.path.exists(data_dir):
    print("No data directory found.")
    sys.exit(1)

# --- Pre-flight: verify Ollama is up before wasting time on every file ---
print("Checking Ollama server...")
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    if r.status_code == 200:
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"  Ollama OK. Available models: {models}")
    else:
        print(f"  Ollama responded with status {r.status_code}. Continuing anyway...")
except Exception:
    print("\nFATAL: Ollama server is not running at http://localhost:11434")
    print("  Please start it first: ollama serve")
    sys.exit(1)

# --- Warm up: load model into RAM so the first real call doesn't cold-start ---
print("Warming up model (llama3.2)...")
try:
    warmup_payload = {"model": "llama3.2", "prompt": "Say OK.", "stream": False, "options": {"num_ctx": 512}}
    wr = requests.post("http://localhost:11434/api/generate", json=warmup_payload, timeout=300)
    if wr.status_code == 200:
        print("  Model warm-up complete.")
    else:
        print(f"  Warm-up returned status {wr.status_code}: {wr.text[:100]}")
except Exception as e:
    print(f"  Warm-up failed: {e}. Continuing anyway...")

files = sorted(os.listdir(data_dir))

def run_file(filename):
    path = os.path.join(data_dir, filename)
    print(f"\n>>> Running pipeline on {filename}...")
    t0 = time.time()
    result = subprocess.run(["python", script_path, path])
    elapsed = time.time() - t0
    status = "OK" if result.returncode == 0 else f"FAILED (exit {result.returncode})"
    print(f"    {filename} -> {status} in {elapsed:.1f}s")
    return elapsed

# First run on demo files to create v1
demo_files = [f for f in files if f.startswith("demo_")]
print(f"\n=== Processing {len(demo_files)} DEMO files ===")
for df in demo_files:
    run_file(df)

# Then run on onboarding files to create v2
onboarding_files = [f for f in files if f.startswith("onboarding_")]
print(f"\n=== Processing {len(onboarding_files)} ONBOARDING files ===")
for of in onboarding_files:
    run_file(of)

print("\n=== Batch processing complete. ===")
