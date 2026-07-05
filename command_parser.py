from models import CommandObject


def parse_commands(dynamic_xml):
    """
    Read every command inside one Dynamic.
    """

    commands = []

    find_commands(dynamic_xml, commands)

    return commands


def find_commands(xml_element, commands):
    """
    Search through the XML looking for GraphWorX commands.
    """

    for child in xml_element:

        tag = clean_tag(child.tag)

        # Is this a command?
        if tag.endswith("Command"):

            command = CommandObject()

            command.command_type = tag

            command.properties = dict(child.attrib)

            commands.append(command)

        # Keep searching deeper
        find_commands(child, commands)


def clean_tag(tag):

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag