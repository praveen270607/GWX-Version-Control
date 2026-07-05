# from parser import parse_gdfx
# from tree import print_display_tree


# display = parse_gdfx("sample/Demo.gdfx")

# print("Display Loaded Successfully!\n")

# print_display_tree(display)


# from parser import parse_gdfx

# display = parse_gdfx("sample/Demo.gdfx")

# stack_panel = display.children[2]

# rectangle = stack_panel.children[4]

# print("Rectangle Name :", rectangle.name)
# print("Rectangle ID   :", rectangle.object_id)
# print()
# print("Parent Type    :", rectangle.parent.object_type)
# print("Parent ID      :", rectangle.parent_id)

from cli import run

run()

# from parser import is_dynamic_element

# print(is_dynamic_element("Rectangle"))
# print(is_dynamic_element("GwxPick"))
# print(is_dynamic_element("GwxDynamicGroup"))