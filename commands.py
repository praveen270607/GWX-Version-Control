from repository import initialize_repository
from parser import parse_gdfx
from serializer import object_to_dict
from snapshot import save_snapshot
from lookup import build_lookup
from compare_engine import compare_objects

from pprint import pprint

def init_command():
    """
    Initialize a new GraphWorX repository.
    """
    initialize_repository()

def add_command(file_path):

    if file_path is None:
        print("Please provide a GraphWorX file.")
        return

    print(f"Opening: {file_path}")

    display = parse_gdfx(file_path)
    snapshot = save_snapshot(display, "000001")
    print(f"Snapshot saved to: {snapshot}")
    data = display.to_dict()
    pprint(data, width=120)
    print("Display Loaded Successfully!") 
    # print(f"Root Object : {display.object_type}")
    # print(f"Object ID   : {display.object_id}")

def compare_command(old_file, new_file):

    print()

    print("Opening old display...")

    old_display = parse_gdfx(old_file)

    print("Opening new display...")

    new_display = parse_gdfx(new_file)

    old_lookup = build_lookup(old_display)

    new_lookup = build_lookup(new_display)

    from matcher.object_matcher import ObjectMatcher

    matcher = ObjectMatcher()

    old_object = old_lookup["/Canvas/StackPanel[1]/Rectangle1"]
    new_object = new_lookup["/Canvas/StackPanel[1]/Rectangle1"]

    result = matcher.match_objects(old_object, new_object)

    print(result.to_dict())
    
    added, removed = compare_objects(
        old_lookup,
        new_lookup
    )

    print()

    print("========== Comparison ==========")

    print()

    print("Added Objects")

    if not added:
        print("None")
    else:
        for obj in added:
            print("+", obj)

    print()

    print("Removed Objects")

    if not removed:
        print("None")
    else:
        for obj in removed:
            print("-", obj)    

  