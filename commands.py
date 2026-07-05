from repository import initialize_repository
from parser import parse_gdfx
from serializer import object_to_dict

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
    data = display.to_dict()
    pprint(data, width=120)
    print("Display Loaded Successfully!") 
    # print(f"Root Object : {display.object_type}")
    # print(f"Object ID   : {display.object_id}")

  