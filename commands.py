from repository import (
    checkout_branch,
    commit,
    create_branch,
    initialize_repository,
    list_branches,
    merge_branch,
    restore_file,
    show_log,
    stage_file,
    stage_remove,
    staged_comparison_paths,
    status
)
from parser import parse_gdfx
from lookup import build_lookup
from compare_engine import compare_objects
from pdf_export import export_comparison_pdf

def init_command():
    """
    Initialize a new GraphWorX repository.
    """
    initialize_repository()

def add_command(file_path):
    stage_file(file_path)


def status_command():
    status()


def branch_command(branch_name):
    if branch_name is None:
        list_branches()
    else:
        create_branch(branch_name)


def checkout_command(branch_name, force=False):
    checkout_branch(branch_name, force=force)


def commit_command(message):
    commit(message)


def diff_command(file_path):
    old_file, new_file = staged_comparison_paths(file_path)
    compare_command(old_file, new_file)


def remove_command(file_path):
    stage_remove(file_path)


def restore_command(file_path):
    restore_file(file_path)


def log_command():
    show_log()


def merge_command(branch_name):
    merge_branch(branch_name)

# def compare_command(old_file, new_file):

#     print()

#     print("Opening old display...")

#     old_display = parse_gdfx(old_file)

#     print("Opening new display...")

#     new_display = parse_gdfx(new_file)

#     old_lookup = build_lookup(old_display)

#     new_lookup = build_lookup(new_display)

#     comparison_result = compare_objects(
#         old_lookup,
#         new_lookup
#     )

#     print()

#     print("========== Comparison ==========")

#     print()

#     print("Added Objects")

#     if not comparison_result.added:
#         print("None")
#     else:
#         for obj in comparison_result.added:
#             print("+", obj)

#     print()

#     print("Removed Objects")

#     if not comparison_result.removed:
#         print("None")
#     else:
#         for obj in comparison_result.removed:
#             print("-", obj)

#     print()

#     print("Modified Objects")

#     if not comparison_result.modified:
#         print("None")
#     else:
#         for pair in comparison_result.pairs:
#             if pair.is_matched() and pair.match_result.differences:
#                 print("~", pair.old_object.object_id)
#                 for difference in pair.match_result.differences:
#                     print("  ", difference)

#     print()

#     print("Unchanged Objects")

#     if not comparison_result.unchanged:
#         print("None")
#     else:
#         for obj in comparison_result.unchanged:
#             print("=", obj)


def compare_command(old_file, new_file):

    # ANSI color codes
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    print()
    print("Opening old display...")

    old_display = parse_gdfx(old_file)

    print("Opening new display...")

    new_display = parse_gdfx(new_file)

    old_lookup = build_lookup(old_display)
    new_lookup = build_lookup(new_display)

    comparison_result = compare_objects(
        old_lookup,
        new_lookup
    )

    print()
    print("========== Comparison ==========")
    print()

    # Added Objects - GREEN
    print(f"{GREEN}Added Objects{RESET}")

    if not comparison_result.added:
        print("None")
    else:
        for obj in comparison_result.added:
            print(f"{GREEN}+ {obj}{RESET}")

    print()

    # Removed Objects - RED
    print(f"{RED}Removed Objects{RESET}")

    if not comparison_result.removed:
        print("None")
    else:
        for obj in comparison_result.removed:
            print(f"{RED}- {obj}{RESET}")

    print()

    # Modified Objects - YELLOW
    print(f"{YELLOW}Modified Objects{RESET}")

    if not comparison_result.modified:
        print("None")
    else:
        for pair in comparison_result.pairs:
            if pair.is_matched() and pair.match_result.differences:
                print(f"{YELLOW}~ {pair.old_object.object_id}{RESET}")

                for difference in pair.match_result.differences:
                    print(f"{YELLOW}  {difference}{RESET}")

    print()

    while True:
        answer = input(
            "Export this change record to PDF? (y/n): "
        ).strip().lower()

        if answer in ("y", "yes"):
            filename = input(
                "Enter PDF filename (press Enter for change_record.pdf): "
            ).strip()

            if not filename:
                filename = "change_record.pdf"
            elif not filename.lower().endswith(".pdf"):
                filename += ".pdf"

            try:
                export_comparison_pdf(
                    comparison_result,
                    filename
                )
            except Exception as error:
                print(f"PDF export failed: {error}")

            break

        elif answer in ("n", "no"):
            print("PDF export skipped.")
            break

        else:
            print("Please enter y or n.")


    # Unchanged Objects - disabled for now
    # print("Unchanged Objects")
    #
    # if not comparison_result.unchanged:
    #     print("None")
    # else:
    #     for obj in comparison_result.unchanged:
    #         print("=", obj)


