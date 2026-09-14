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

            command.parameters = parse_parameters(child)

            commands.append(command)

        # Keep searching deeper
        find_commands(child, commands)


def clean_tag(tag):

    if "}" in tag:
        return tag.split("}", 1)[1]

    return tag


def parse_parameters(command_xml):
    """
    Flatten attributes inside a command into named parameters.

    Command attributes remain in ``properties``. Attributes nested below the
    command are parameters, and their XML path keeps similarly named values
    unambiguous.
    """

    parameters = {}

    def visit(element, path):

        for child in element:

            tag = clean_tag(child.tag)
            child_path = f"{path}/{tag}"

            for name, value in child.attrib.items():
                parameters[f"{child_path}/{name}"] = value

            visit(child, child_path)

    visit(command_xml, "")

    return parameters
