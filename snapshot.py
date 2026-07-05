from pathlib import Path
import json

from serializer import object_to_dict


def save_snapshot(display_object, snapshot_name):
    """
    Save one parsed display as a JSON snapshot.
    """

    snapshot_folder = Path(".gwx") / "versions"

    snapshot_folder.mkdir(parents=True, exist_ok=True)

    snapshot_file = snapshot_folder / f"{snapshot_name}.json"

    data = object_to_dict(display_object)

    with open(snapshot_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return snapshot_file