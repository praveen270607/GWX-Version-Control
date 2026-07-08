def build_lookup(display_object):
    """
    Build a dictionary using object_id as the key.
    """

    lookup = {}

    add_to_lookup(display_object, lookup)

    return lookup


def add_to_lookup(display_object, lookup):
    """
    Add this object and all its children.
    """

    lookup[display_object.object_id] = display_object

    for child in display_object.children:

        add_to_lookup(child, lookup)