import os
import sys
import datetime

log_file_path = os.path.join(os.path.dirname(__file__), "test_output.log")

try:
    with open(log_file_path, "w", encoding="utf-8") as f:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] Hello from test_log_creation.py!\n")
        f.write(f"[{timestamp}] Python version: {sys.version}\n")
        f.write(f"[{timestamp}] Current working directory: {os.getcwd()}\n")
    print(f"Successfully wrote to {log_file_path}")
except Exception as e:
    # If we can't write to file, try printing to standard error
    # This might still not show in VSCode terminal if it's a terminal issue
    # but it's worth a try.
    sys.stderr.write(f"Error creating log file: {e}\n")
    sys.stderr.flush()
    print(f"Error creating log file: {e}") # Also print to stdout
