import sys
from commands import init_command, add_command

def run():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        return

    command = sys.argv[1]

    # Read the file name if the user provided one
    file_path = None

    if len(sys.argv) > 2:
        file_path = sys.argv[2]

    if command == "init":
        init_command()

    elif command == "add":
        add_command(file_path)

    else:
        print(f"Unknown command: {command}")