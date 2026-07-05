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

            "dynamics": [],

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

    def __init__(self):

        # Example: Pick, Hide, Color
        self.dynamic_type = ""

        # Dynamic settings
        self.properties = {}

        # Commands like LoadDisplayCommand
        self.commands = []

        # Optional description
        self.description = ""

    def add_command(self, command):

        self.commands.append(command)

class CommandObject:

    def __init__(self):

        # Example:
        # LoadDisplayCommand
        # WriteValueCommand
        # SetDataPointCommand

        self.command_type = ""

        # Command settings
        self.properties = {}

        # Future support
        self.parameters = {}        