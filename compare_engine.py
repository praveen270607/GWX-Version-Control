def compare_objects(old_objects, new_objects):
    """
    Compare the objects in two displays.
    """

    added = []
    removed = []

    old_ids = set(old_objects.keys())
    new_ids = set(new_objects.keys())

    # Objects added
    for object_id in new_ids - old_ids:
        added.append(object_id)

    # Objects removed
    for object_id in old_ids - new_ids:
        removed.append(object_id)

    return added, removed