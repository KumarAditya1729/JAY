#!/usr/bin/env python3
import sys
import subprocess
import requests

API_URL = "http://localhost:8001/observation/"


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run":
        print("Usage: jay run <command>")
        sys.exit(1)

    command = " ".join(sys.argv[2:])

    # Run the command and capture output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Print to user so they see it normally
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    # Send passive observation to JAY
    payload = {
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }

    try:
        requests.post(
            API_URL,
            json={"source": "Terminal", "payload": payload},
            headers={"Authorization": "Bearer dev_key_only_change_in_prod"},
            timeout=2.0,
        )
    except Exception:
        # Silently fail if JAY is down
        pass


if __name__ == "__main__":
    main()
