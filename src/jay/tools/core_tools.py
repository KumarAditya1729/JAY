import os
import subprocess

def read_file(arguments: dict) -> str:
    path = arguments.get("path")
    if not path or not os.path.exists(path):
        return f"Error: File {path} does not exist."
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(arguments: dict) -> str:
    path = arguments.get("path")
    content = arguments.get("content", "")
    if not path:
        return "Error: Path is required."
    try:
        with open(path, "w") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def search_files(arguments: dict) -> str:
    directory = arguments.get("directory", ".")
    pattern = arguments.get("pattern", "*")
    cmd = f"find {directory} -name '{pattern}'"
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return res.stdout.strip() if res.stdout.strip() else "No files found."
    except Exception as e:
        return f"Error searching files: {e}"

def git_status(arguments: dict) -> str:
    try:
        res = subprocess.run("git status", shell=True, capture_output=True, text=True, timeout=10)
        return res.stdout.strip()
    except Exception as e:
        return f"Error checking git status: {e}"

def system_command_blocked(arguments: dict) -> str:
    return "Error: Action blocked by ExecutionPolicyEngine."
