import sys
from commands import (
    init_command,
    add_command,
    branch_command,
    checkout_command,
    commit_command,
    compare_command,
    diff_command,
    status_command
)
from repository import RepositoryError

def run():
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        return

    command = sys.argv[1]
    arguments = sys.argv[2:]

    try:
        if command == "init" and not arguments:
            init_command()

        elif command == "add" and len(arguments) == 1:
            add_command(arguments[0])

        elif command == "status" and not arguments:
            status_command()

        elif command == "branch":
            branch_command(arguments[0] if arguments else None)

        elif command == "checkout" and len(arguments) == 1:
            checkout_command(arguments[0])

        elif command == "diff" and len(arguments) == 1:
            diff_command(arguments[0])

        elif command == "commit" and len(arguments) == 2 and arguments[0] == "-m":
            commit_command(arguments[1])

        elif command == "compare" and len(arguments) == 2:
            compare_command(arguments[0], arguments[1])

        else:
            print_usage()

    except RepositoryError as error:
        print(f"Error: {error}")


def print_usage():

    print("Usage:")
    print("  python main.py init")
    print("  python main.py status")
    print("  python main.py branch [name]")
    print("  python main.py checkout <branch>")
    print("  python main.py add <file.gdfx>")
    print("  python main.py diff <file.gdfx>")
    print("  python main.py commit -m \"message\"")
    print("  python main.py compare <old.gdfx> <new.gdfx>")
