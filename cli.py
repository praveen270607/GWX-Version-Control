import sys
from commands import (
    init_command,
    add_command,
    branch_command,
    checkout_command,
    commit_command,
    compare_command,
    diff_command,
    log_command,
    merge_command,
    remove_command,
    restore_command,
    status_command
)
from repository import RepositoryError

def run():
    if len(sys.argv) < 2:
        print_usage()
        return 2

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

        elif command == "checkout" and (
            len(arguments) == 1 or (len(arguments) == 2 and arguments[0] == "-f")
        ):
            force = arguments[0] == "-f"
            branch_name = arguments[1] if force else arguments[0]
            checkout_command(branch_name, force)

        elif command == "diff" and len(arguments) == 1:
            diff_command(arguments[0])

        elif command == "rm" and len(arguments) == 1:
            remove_command(arguments[0])

        elif command == "restore" and len(arguments) == 1:
            restore_command(arguments[0])

        elif command == "log" and not arguments:
            log_command()

        elif command == "merge" and len(arguments) == 1:
            merge_command(arguments[0])

        elif command == "commit" and len(arguments) == 2 and arguments[0] == "-m":
            commit_command(arguments[1])

        elif command == "compare" and len(arguments) == 2:
            compare_command(arguments[0], arguments[1])

        else:
            print_usage()
            return 2

    except RepositoryError as error:
        print(f"Error: {error}")
        return 1

    return 0


def print_usage():

    print("Usage:")
    print("  python main.py init")
    print("  python main.py status")
    print("  python main.py branch [name]")
    print("  python main.py checkout [-f] <branch>")
    print("  python main.py add <file.gdfx>")
    print("  python main.py diff <file.gdfx>")
    print("  python main.py rm <file>")
    print("  python main.py restore <file>")
    print("  python main.py commit -m \"message\"")
    print("  python main.py log")
    print("  python main.py merge <branch>")
    print("  python main.py compare <old.gdfx> <new.gdfx>")
