def object_to_dict(display_object):

    data = {}

    data["object_id"] = display_object.object_id
    data["object_type"] = display_object.object_type
    data["name"] = display_object.name
    data["parent_id"] = display_object.parent_id

    return data