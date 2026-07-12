from parser import parse_gdfx
from lookup import build_lookup
from matcher.object_matcher import ObjectMatcher

display = parse_gdfx("sample/Demo.gdfx")

lookup = build_lookup(display)

old_object = lookup["/Canvas/StackPanel[1]/Rectangle1"]

new_object = lookup["/Canvas/StackPanel[1]/Rectangle1"]

matcher = ObjectMatcher()

result = matcher.match_objects(old_object, new_object)

print(result.to_dict())