import sys
from commands import (
    init_command,
    add_command,
    compare_command
)

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

    elif command == "compare":

        if len(sys.argv) != 4:
            print("Usage:")
            print("python main.py compare old.gdfx new.gdfx")
            return

        compare_command(
            sys.argv[2],
            sys.argv[3]
        )

    else:
        print(f"Unknown command: {command}")