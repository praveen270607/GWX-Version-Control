from models import DynamicObject
from command_parser import parse_commands


def parse_dynamic(xml_element):
    """
    Parse one GraphWorX Dynamic.
    """

    dynamic = DynamicObject()

    dynamic_element = find_real_dynamic(xml_element)

    if dynamic_element is None:
        return None

    dynamic.dynamic_type = clean_tag(dynamic_element.tag)

    dynamic.properties = dict(dynamic_element.attrib)

    # Ask the Command Parser to find commands
    commands = parse_commands(dynamic_element)

    for command in commands:
        dynamic.add_command(command)

    return dynamic


def find_real_dynamic(xml_element):
    """
    Recursively search until we find the real
    GraphWorX Dynamic.
    """

    element_name = clean_tag(xml_element.tag)

    # If this is a real Dynamic, return it
    if (
        element_name.startswith("GwxPick")
        or element_name.startswith("GwxHide")
        or element_name.startswith("GwxColor")
        or element_name.startswith("GwxRotation")
        or element_name.startswith("GwxResize")
        or element_name.startswith("GwxAnimation")
        or element_name.startswith("GwxProcessPoint")
    ):
        return xml_element

    # Otherwise keep searching inside children
    for child in xml_element:

        result = find_real_dynamic(child)

        if result is not None:
            return result

    return None


def clean_tag(tag):

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag