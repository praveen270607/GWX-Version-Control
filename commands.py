from repository import (
    checkout_branch,
    commit,
    create_branch,
    initialize_repository,
    list_branches,
    stage_file,
    staged_comparison_paths,
    status
)
from parser import parse_gdfx
from lookup import build_lookup
from compare_engine import compare_objects

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


def checkout_command(branch_name):
    checkout_branch(branch_name)


def commit_command(message):
    commit(message)


def diff_command(file_path):
    old_file, new_file = staged_comparison_paths(file_path)
    compare_command(old_file, new_file)

def compare_command(old_file, new_file):

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

    print("Added Objects")

    if not comparison_result.added:
        print("None")
    else:
        for obj in comparison_result.added:
            print("+", obj)

    print()

    print("Removed Objects")

    if not comparison_result.removed:
        print("None")
    else:
        for obj in comparison_result.removed:
            print("-", obj)

    print()

    print("Modified Objects")

    if not comparison_result.modified:
        print("None")
    else:
        for pair in comparison_result.pairs:
            if pair.is_matched() and pair.match_result.differences:
                print("~", pair.old_object.object_id)
                for difference in pair.match_result.differences:
                    print("  ", difference)

    print()

    print("Unchanged Objects")

    if not comparison_result.unchanged:
        print("None")
    else:
        for obj in comparison_result.unchanged:
            print("=", obj)

