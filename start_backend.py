import subprocess
import sys
import os

# Change to backend directory
os.chdir(r"D:\3_Code\opencode_workspace\home-assets-trace\backend")

# Start uvicorn
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

print(f"Backend started with PID: {process.pid}")
print("Waiting for startup...")

# Read output for a few seconds
import time
time.sleep(3)

# Print any output
for line in process.stdout:
    print(line.strip())
    if "Application startup complete" in line:
        print("\nBackend is running at http://localhost:8000")
        print("Press Ctrl+C to stop")
        break

# Keep the script running
try:
    process.wait()
except KeyboardInterrupt:
    print("\nStopping backend...")
    process.terminate()
