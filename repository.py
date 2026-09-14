"""Persistent repository operations for GraphWorX version control."""

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil


REPOSITORY_DIRECTORY = ".gwx"


class RepositoryError(Exception):
    """Raised when a repository operation cannot be completed safely."""


def repository_path(root=None):

    root = Path(root or Path.cwd())
    return root / REPOSITORY_DIRECTORY


def initialize_repository(root=None, announce=True):
    """Create a repository, or upgrade an early prototype repository safely."""

    root = Path(root or Path.cwd())
    repo = repository_path(root)
    existed = repo.exists()

    (repo / "objects").mkdir(parents=True, exist_ok=True)
    (repo / "commits").mkdir(parents=True, exist_ok=True)
    (repo / "refs").mkdir(parents=True, exist_ok=True)
    (repo / "locks").mkdir(parents=True, exist_ok=True)

    head_file = repo / "HEAD"
    if not head_file.exists():
        head_file.write_text("main", encoding="utf-8")

    config_file = repo / "config.json"
    config = read_json(config_file) if config_file.exists() else {}
    config.update({
        "repository_name": root.name,
        "format_version": 2,
        "current_branch": current_branch(root)
    })
    write_json(config_file, config)

    if not branch_ref_path(current_branch(root), root).exists():
        write_json(branch_ref_path(current_branch(root), root), {"head": None})

    if announce:
        print("Repository is ready." if existed else "Repository initialized successfully.")


def ensure_repository(root=None):

    if not repository_path(root).exists():
        raise RepositoryError(
            "Not a GraphWorX repository. Run 'python main.py init' first."
        )

    initialize_repository(root, announce=False)


def current_branch(root=None):

    head_file = repository_path(root) / "HEAD"
    if not head_file.exists():
        return "main"

    return head_file.read_text(encoding="utf-8").strip() or "main"


def branch_ref_path(branch_name, root=None):

    validate_branch_name(branch_name)
    return repository_path(root) / "refs" / f"{branch_name}.json"


def get_branch_head(branch_name=None, root=None):

    branch_name = branch_name or current_branch(root)
    ref_file = branch_ref_path(branch_name, root)

    if not ref_file.exists():
        raise RepositoryError(f"Branch '{branch_name}' does not exist.")

    return read_json(ref_file).get("head")


def create_branch(branch_name, root=None):

    ensure_repository(root)
    ref_file = branch_ref_path(branch_name, root)

    if ref_file.exists():
        raise RepositoryError(f"Branch '{branch_name}' already exists.")

    write_json(ref_file, {"head": get_branch_head(root=root)})
    print(f"Created branch '{branch_name}'.")


def list_branches(root=None):

    ensure_repository(root)
    branch = current_branch(root)

    for ref_file in sorted((repository_path(root) / "refs").glob("*.json")):
        name = ref_file.stem
        marker = "*" if name == branch else " "
        head = read_json(ref_file).get("head") or "(no commits)"
        print(f"{marker} {name} {head}")


def checkout_branch(branch_name, root=None):
    """Switch the active branch without overwriting the user's working files."""

    ensure_repository(root)
    get_branch_head(branch_name, root)

    repo = repository_path(root)
    (repo / "HEAD").write_text(branch_name, encoding="utf-8")

    config_file = repo / "config.json"
    config = read_json(config_file)
    config["current_branch"] = branch_name
    write_json(config_file, config)

    print(f"Switched to branch '{branch_name}'.")
    print("Working files were not replaced; stage the files you want to commit.")


def stage_file(file_path, root=None):
    """Store a new immutable blob and record the branch revision it is based on."""

    ensure_repository(root)
    root = Path(root or Path.cwd()).resolve()
    source = Path(file_path).resolve()

    if not source.is_file():
        raise RepositoryError(f"File not found: {file_path}")

    try:
        relative_path = source.relative_to(root).as_posix()
    except ValueError as error:
        raise RepositoryError("Only files inside this repository can be staged.") from error

    blob_id = store_blob(source, root)
    tree = current_tree(root)
    base_revision = tree.get(relative_path, {}).get("revision")
    index = load_index(root)

    index[relative_path] = {
        "base_revision": base_revision,
        "new_blob": blob_id
    }
    save_index(index, root)

    if base_revision is None:
        print(f"Staged new file: {relative_path}")
    else:
        print(f"Staged update to {relative_path} based on revision {base_revision}.")


def status(root=None):

    ensure_repository(root)
    branch = current_branch(root)
    head = get_branch_head(branch, root) or "(no commits)"
    index = load_index(root)

    print(f"On branch {branch}")
    print(f"HEAD: {head}")

    if not index:
        print("Nothing staged.")
        return

    print("Staged changes:")
    for path, entry in sorted(index.items()):
        base = entry["base_revision"] or "new file"
        print(f"  {path} (base: {base})")


def commit(message, root=None):
    """Commit staged files only if their recorded base revisions are current."""

    ensure_repository(root)

    if not message:
        raise RepositoryError("A commit message is required. Use: commit -m \"message\"")

    with commit_lock(root):
        index = load_index(root)
        if not index:
            raise RepositoryError("Nothing staged to commit.")

        branch = current_branch(root)
        parent = get_branch_head(branch, root)
        tree = load_tree(parent, root)

        conflicts = []
        for path, entry in index.items():
            current_revision = tree.get(path, {}).get("revision")
            if current_revision != entry["base_revision"]:
                conflicts.append((path, entry["base_revision"], current_revision))

        if conflicts:
            details = "; ".join(
                f"{path}: staged from {base or 'new file'}, current is {current or 'new file'}"
                for path, base, current in conflicts
            )
            raise RepositoryError(
                "Commit rejected because the staged base revision is no longer current. "
                f"Re-compare and stage again. {details}"
            )

        commit_id = next_commit_id(root)
        for path, entry in index.items():
            tree[path] = {
                "blob": entry["new_blob"],
                "revision": commit_id
            }

        commit_data = {
            "id": commit_id,
            "parent": parent,
            "branch": branch,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tree": tree
        }
        write_json(repository_path(root) / "commits" / f"{commit_id}.json", commit_data)
        write_json(branch_ref_path(branch, root), {"head": commit_id})
        save_index({}, root)

    print(f"Committed {commit_id}: {message}")


def staged_comparison_paths(file_path, root=None):
    """Return the old and new blob paths for a staged file, if it has a base."""

    ensure_repository(root)
    root = Path(root or Path.cwd()).resolve()
    source = Path(file_path).resolve()

    try:
        relative_path = source.relative_to(root).as_posix()
    except ValueError as error:
        raise RepositoryError("Only files inside this repository can be compared.") from error

    entry = load_index(root).get(relative_path)
    if entry is None:
        raise RepositoryError("File is not staged. Run add before diff.")

    if entry["base_revision"] is None:
        raise RepositoryError("This is a new file; it has no previous version to compare.")

    tree = current_tree(root)
    old_blob = tree[relative_path]["blob"]
    return blob_path(old_blob, root), blob_path(entry["new_blob"], root)


def current_tree(root=None):

    return load_tree(get_branch_head(root=root), root)


def load_tree(commit_id, root=None):

    if commit_id is None:
        return {}

    return read_json(repository_path(root) / "commits" / f"{commit_id}.json")["tree"]


def store_blob(source, root=None):

    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    destination = blob_path(digest, root, source.suffix)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if not destination.exists():
        shutil.copy2(source, destination)

    return digest


def blob_path(blob_id, root=None, suffix=None):

    objects = repository_path(root) / "objects"
    matches = list(objects.glob(f"{blob_id}.*"))

    if matches:
        return matches[0]

    if suffix is None:
        raise RepositoryError(f"Stored object '{blob_id}' is missing.")

    return objects / f"{blob_id}{suffix}"


def load_index(root=None):

    index_file = repository_path(root) / "index.json"
    return read_json(index_file) if index_file.exists() else {}


def save_index(index, root=None):

    write_json(repository_path(root) / "index.json", index)


def next_commit_id(root=None):

    commit_ids = [
        int(file.stem)
        for file in (repository_path(root) / "commits").glob("*.json")
        if file.stem.isdigit()
    ]
    return f"{max(commit_ids, default=0) + 1:06d}"


@contextmanager
def commit_lock(root=None):

    lock_file = repository_path(root) / "locks" / "commit.lock"

    try:
        descriptor = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as error:
        raise RepositoryError("Another commit is in progress. Try again shortly.") from error

    try:
        os.close(descriptor)
        yield
    finally:
        lock_file.unlink(missing_ok=True)


def validate_branch_name(branch_name):

    if not branch_name or not branch_name.replace("-", "").replace("_", "").isalnum():
        raise RepositoryError(
            "Branch names may contain only letters, numbers, hyphens, and underscores."
        )


def read_json(path):

    with open(path, encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(f"{path.suffix}.tmp")

    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, sort_keys=True)

    temporary_path.replace(path)
