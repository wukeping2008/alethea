import os
import datetime

file_path = os.path.join(os.path.dirname(__file__), "temp_output.log")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"[{timestamp}] This is a test message from temp_test_write.py.\n")
    print(f"Successfully wrote to {file_path}")
except Exception as e:
    print(f"Error writing to file: {e}")
