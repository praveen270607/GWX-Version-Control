def print_display_tree(obj, level=0):

    indent = "    " * level

    if obj.name:
        print(f"{indent}- {obj.object_type} ({obj.name})")
    else:
        print(f"{indent}- {obj.object_type}")

    print(f"{indent}  ID : {obj.object_id}")

    for child in obj.children:
        print_display_tree(child, level + 1)