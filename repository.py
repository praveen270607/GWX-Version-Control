from pathlib import Path
import json


def initialize_repository():

    repo = Path(".gwx")

    if repo.exists():
        print("Repository already exists.")
        return

    # Create folders
    (repo / "branches" / "main").mkdir(parents=True)
    (repo / "versions").mkdir()
    (repo / "index").mkdir()
    (repo / "logs").mkdir()

    # Create HEAD
    (repo / "HEAD").write_text("main")

    # Create config.json
    config = {
        "repository_name": Path.cwd().name,
        "version": "1.0",
        "current_branch": "main"
    }

    with open(repo / "config.json", "w") as f:
        json.dump(config, f, indent=4)

    print("Repository initialized successfully.")