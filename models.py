class DisplayObject:
    """
    Represents one object inside a GraphWorX display.
    """

    def __init__(self):

        # Unique object ID
        self.object_id = ""

        # Object type
        self.object_type = ""

        # Object name
        self.name = ""

        # All properties
        self.properties = {}

        # Parent object
        self.parent = None

        # Parent object ID
        self.parent_id = ""

        # Child objects
        self.children = []

        # Dynamics
        self.dynamics = []

    def to_dict(self):

        data = {

            "object_id": self.object_id,

            "object_type": self.object_type,

            "name": self.name,

            "parent_id": self.parent_id,

            "properties": self.properties,

            "dynamics": [
                dynamic.to_dict()
                for dynamic in self.dynamics
            ],

            "children": []

        }

        # Convert every child into a dictionary
        for child in self.children:

            data["children"].append(child.to_dict())

        return data 
    
    def add_child(self, child):

        self.children.append(child)

    def add_dynamic(self, dynamic):

        self.dynamics.append(dynamic)
        
    def __str__(self):
        return f"{self.object_type} ({self.name})"
    
class DynamicObject:
    """
    Represents one GraphWorX Dynamic.
    Example:
        Pick
        Hide
        Color
        Rotation
    """

    def __init__(self):

        # Type of Dynamic
        self.dynamic_type = ""

        # Dynamic properties
        self.properties = {}

        # Commands inside the Dynamic
        self.commands = []

        # Optional description
        self.description = ""

    def add_command(self, command):
        """
        Add a command to this Dynamic.
        """
        self.commands.append(command)

    def to_dict(self):

        return {

            "dynamic_type": self.dynamic_type,

            "description": self.description,

            "properties": self.properties,

            "commands": [
                command.to_dict()
                for command in self.commands
            ]
        }

class CommandObject:
    """
    Represents one command inside a Dynamic.
    Example:
        LoadDisplayCommand
        WriteValueCommand
        SetDataPointCommand
    """

    def __init__(self):

        self.command_type = ""

        self.properties = {}

        self.parameters = {}

    def to_dict(self):

        return {

            "command_type": self.command_type,

            "properties": self.properties,

            "parameters": self.parameters
        }      