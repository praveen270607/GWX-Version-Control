from models import DisplayObject, DynamicObject
import xml.etree.ElementTree as ET

def is_dynamic_element(element_name):
    """
    Returns True if this XML element belongs to GraphWorX Dynamics.
    """

    dynamic_prefixes = [
        "GwxDynamicGroup",
        "GwxPick",
        "GwxAnimation",
        "GwxHide",
        "GwxColor",
        "GwxRotation",
        "GwxResize",
        "GwxProcessPoint"
    ]

    return any(
        element_name.startswith(prefix)
        for prefix in dynamic_prefixes
    )

def create_dynamic_object(element):

    dynamic = DynamicObject()

    dynamic.dynamic_type = element.tag.split("}")[-1]

    dynamic.properties = dict(element.attrib)

    return dynamic

def clean_tag(tag):
    """
    Removes the XML namespace.
    """
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def create_display_object(xml_element, parent_path=""):

    obj = DisplayObject()

    obj.object_type = clean_tag(xml_element.tag)

    # Read the object name first
    obj.name = xml_element.attrib.get("Name", "")

    # The parent already calculated the correct object ID
    # Root object
    if parent_path == "":
        obj.object_id = f"/{obj.object_type}"
    else:
        obj.object_id = parent_path

    # Store all properties
    obj.properties = dict(xml_element.attrib)

    # Count how many child objects of each type we have seen
    child_counts = {}

    # Read every child object
    for child in xml_element:

        child_type = clean_tag(child.tag)

        print(child_type)

        if child_type not in child_counts:
            child_counts[child_type] = 1
        else:
            child_counts[child_type] += 1

        # Build the child's path

        child_name = child.attrib.get("Name", "")

        if child_name:
            child_path = f"{obj.object_id}/{child_name}"
        else:
            child_path = (
                f"{obj.object_id}/{child_type}"
                f"[{child_counts[child_type]}]"
            )

        # Is this child actually a GraphWorX Dynamic?
        if is_dynamic_element(child_type):

            dynamic = create_dynamic_object(child)

            obj.dynamics.append(dynamic)

        else:

            child_object = create_display_object(child, child_path)

            # Tell the child who its parent is
            child_object.parent = obj
            child_object.parent_id = obj.object_id

            # Add the child to the parent's list
            obj.children.append(child_object)

    return obj

def parse_gdfx(file_path):

    tree = ET.parse(file_path)

    root = tree.getroot()

    return create_display_object(root)