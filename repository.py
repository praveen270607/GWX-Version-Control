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
        "format_version": 3,
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


def checkout_branch(branch_name, root=None, force=False):
    """Switch branches and restore tracked files without discarding local edits."""

    ensure_repository(root)
    target_head = get_branch_head(branch_name, root)

    if branch_name == current_branch(root):
        print(f"Already on branch '{branch_name}'.")
        return

    if load_index(root) and not force:
        raise RepositoryError("Cannot checkout with staged changes. Commit or unstage them first.")

    changed_files = working_changes(root)
    if changed_files and not force:
        raise RepositoryError(
            "Cannot checkout because tracked files have uncommitted changes: "
            + ", ".join(changed_files)
        )

    write_working_tree(load_tree(target_head, root), root)

    repo = repository_path(root)
    (repo / "HEAD").write_text(branch_name, encoding="utf-8")

    config_file = repo / "config.json"
    config = read_json(config_file)
    config["current_branch"] = branch_name
    write_json(config_file, config)

    print(f"Switched to branch '{branch_name}' at {target_head or '(no commits)'}.")


def stage_file(file_path, root=None):
    """Store a new blob and record the file version it is based on."""

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
    base_file_revision = file_revision(tree.get(relative_path))
    index = load_index(root)

    index[relative_path] = {
        "base_file_revision": base_file_revision,
        "new_blob": blob_id
    }
    save_index(index, root)

    if base_file_revision is None:
        print(f"Staged new file: {relative_path}")
    else:
        print(
            f"Staged update to {relative_path} "
            f"based on file version {base_file_revision}."
        )


def stage_remove(file_path, root=None):
    """Stage deletion of a file currently tracked by the active branch."""

    ensure_repository(root)
    root = Path(root or Path.cwd()).resolve()
    relative_path = normalise_relative_path(file_path, root)
    tree = current_tree(root)

    if relative_path not in tree:
        raise RepositoryError(f"File is not tracked: {relative_path}")

    index = load_index(root)
    index[relative_path] = {
        "base_file_revision": file_revision(tree[relative_path]),
        "new_blob": None
    }
    save_index(index, root)

    source = root / relative_path
    if source.exists():
        source.unlink()

    print(f"Staged deletion: {relative_path}")


def status(root=None):

    ensure_repository(root)
    branch = current_branch(root)
    head = get_branch_head(branch, root) or "(no commits)"
    index = load_index(root)

    print(f"On branch {branch}")
    print(f"HEAD: {head}")

    tree = current_tree(root)
    if tree:
        print("Tracked files:")
        for path, entry in sorted(tree.items()):
            print(
                f"  {path} (file version: {file_revision(entry)}, "
                f"last commit: {last_commit(entry)})"
            )

    if not index:
        print("Nothing staged.")
    else:
        print("Staged changes:")
        for path, entry in sorted(index.items()):
            base = staged_base_file_revision(entry) or "new file"
            action = "delete" if entry["new_blob"] is None else "update"
            print(f"  {action}: {path} (base file version: {base})")

    changed_files = working_changes(root)
    if changed_files:
        print("Unstaged tracked changes:")
        for path in changed_files:
            print(f"  {path}")


def commit(message, root=None):
    """Commit staged files only if their recorded base file versions are current."""

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
            current_revision = file_revision(tree.get(path))
            base_revision = staged_base_file_revision(entry)
            if current_revision != base_revision:
                conflicts.append((path, base_revision, current_revision))

        if conflicts:
            details = "; ".join(
                f"{path}: staged from file version {base or 'new'}, "
                f"current is {current or 'new'}"
                for path, base, current in conflicts
            )
            raise RepositoryError(
                "Commit rejected because the staged base file version is no longer current. "
                f"Re-compare and stage again. {details}"
            )

        commit_id = next_commit_id(root)
        changes = []
        for path, entry in index.items():
            previous_version = file_revision(tree.get(path)) or 0
            if entry["new_blob"] is None:
                tree.pop(path, None)
                changes.append({
                    "path": path,
                    "action": "delete",
                    "from_file_version": previous_version,
                    "to_file_version": None
                })
            else:
                next_file_version = previous_version + 1
                tree[path] = {
                    "blob": entry["new_blob"],
                    "file_revision": next_file_version,
                    "last_commit": commit_id
                }
                changes.append({
                    "path": path,
                    "action": "add" if previous_version == 0 else "update",
                    "from_file_version": previous_version or None,
                    "to_file_version": next_file_version
                })

        commit_data = {
            "id": commit_id,
            "parent": parent,
            "branch": branch,
            "message": message,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "changes": changes,
            "tree": tree
        }
        write_json(repository_path(root) / "commits" / f"{commit_id}.json", commit_data)
        write_json(branch_ref_path(branch, root), {"head": commit_id})
        save_index({}, root)

    print(f"Committed {commit_id}: {message}")


def show_log(root=None):

    ensure_repository(root)
    commit_id = get_branch_head(root=root)

    if commit_id is None:
        print("No commits yet.")
        return

    while commit_id is not None:
        data = load_commit(commit_id, root)
        print(f"{data['id']} {data['created_at']} {data['message']}")
        for change in data.get("changes", describe_changes(data, root)):
            print(
                f"  {change['action']}: {change['path']} "
                f"(file version {change['from_file_version'] or '-'} "
                f"-> {change['to_file_version'] or '-'})"
            )
        commit_id = data.get("parent")


def restore_file(file_path, root=None):
    """Restore a tracked file from the current branch HEAD."""

    ensure_repository(root)
    root = Path(root or Path.cwd()).resolve()
    relative_path = normalise_relative_path(file_path, root)

    if relative_path in load_index(root):
        raise RepositoryError("Cannot restore a staged file. Commit or unstage it first.")

    tree = current_tree(root)
    entry = tree.get(relative_path)
    if entry is None:
        raise RepositoryError(f"File is not tracked at HEAD: {relative_path}")

    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(blob_path(entry["blob"], root), destination)
    print(
        f"Restored {relative_path} from file version {file_revision(entry)} "
        f"(commit {last_commit(entry)})."
    )


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

    if staged_base_file_revision(entry) is None:
        raise RepositoryError("This is a new file; it has no previous version to compare.")

    tree = current_tree(root)
    old_blob = tree[relative_path]["blob"]
    return blob_path(old_blob, root), blob_path(entry["new_blob"], root)


def file_revision(entry):
    """Return a file-local revision, including compatibility with format 2 trees."""

    if entry is None:
        return None

    if "file_revision" in entry:
        return entry["file_revision"]

    # Version 2 recorded only the commit that last changed a file. A file that
    # exists in that format is treated as version 1 when the repository upgrades.
    return 1


def last_commit(entry):

    if entry is None:
        return None

    return entry.get("last_commit", entry.get("revision"))


def staged_base_file_revision(entry):
    """Read format 3 index data, with a safe fallback for an old empty base."""

    if "base_file_revision" in entry:
        return entry["base_file_revision"]

    # An old staged item is deliberately treated as stale when it targeted an
    # existing format 2 file. The user must stage it again after upgrading.
    return None if entry.get("base_revision") is None else "stale-format-2"


def describe_changes(commit_data, root=None):
    """Derive a readable change list for commits created before format 3."""

    before = load_tree(commit_data.get("parent"), root)
    after = commit_data["tree"]
    changes = []

    for path in sorted(set(before) | set(after)):
        old_entry = before.get(path)
        new_entry = after.get(path)
        if entry_blob(old_entry) == entry_blob(new_entry):
            continue

        changes.append({
            "path": path,
            "action": "delete" if new_entry is None else "add" if old_entry is None else "update",
            "from_file_version": file_revision(old_entry),
            "to_file_version": file_revision(new_entry)
        })

    return changes


def current_tree(root=None):

    return load_tree(get_branch_head(root=root), root)


def load_tree(commit_id, root=None):

    if commit_id is None:
        return {}

    return load_commit(commit_id, root)["tree"]


def load_commit(commit_id, root=None):

    commit_file = repository_path(root) / "commits" / f"{commit_id}.json"
    if not commit_file.exists():
        raise RepositoryError(f"Commit '{commit_id}' is missing.")

    return read_json(commit_file)


def merge_branch(branch_name, root=None):
    """Fast-forward or three-way merge a branch without overwriting conflicts."""

    ensure_repository(root)
    current = current_branch(root)
    if branch_name == current:
        raise RepositoryError("Cannot merge a branch into itself.")

    if load_index(root):
        raise RepositoryError("Cannot merge with staged changes. Commit or unstage them first.")

    changed_files = working_changes(root)
    if changed_files:
        raise RepositoryError(
            "Cannot merge with uncommitted tracked changes: " + ", ".join(changed_files)
        )

    ours = get_branch_head(current, root)
    theirs = get_branch_head(branch_name, root)

    if theirs is None:
        print(f"Nothing to merge from '{branch_name}'.")
        return

    if ours is None or is_ancestor(ours, theirs, root):
        write_working_tree(load_tree(theirs, root), root)
        write_json(branch_ref_path(current, root), {"head": theirs})
        print(f"Fast-forwarded '{current}' to {theirs}.")
        return

    if is_ancestor(theirs, ours, root):
        print("Already up to date.")
        return

    base = common_ancestor(ours, theirs, root)
    merged_tree, conflicts = merge_trees(
        load_tree(base, root),
        load_tree(ours, root),
        load_tree(theirs, root)
    )

    if conflicts:
        raise RepositoryError(
            "Merge stopped because both branches changed the same file(s): "
            + ", ".join(conflicts)
            + ". Resolve the display manually, compare it, then stage and commit it."
        )

    with commit_lock(root):
        if get_branch_head(current, root) != ours:
            raise RepositoryError("Branch changed while merging. Try again.")

        commit_id = next_commit_id(root)
        data = {
            "id": commit_id,
            "parent": ours,
            "merge_parent": theirs,
            "branch": current,
            "message": f"Merge branch '{branch_name}'",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tree": merged_tree
        }
        write_json(repository_path(root) / "commits" / f"{commit_id}.json", data)
        write_working_tree(merged_tree, root)
        write_json(branch_ref_path(current, root), {"head": commit_id})

    print(f"Merged '{branch_name}' into '{current}' as {commit_id}.")


def merge_trees(base, ours, theirs):

    merged = {}
    conflicts = []

    for path in sorted(set(base) | set(ours) | set(theirs)):
        base_entry = base.get(path)
        our_entry = ours.get(path)
        their_entry = theirs.get(path)
        base_blob = entry_blob(base_entry)
        our_blob = entry_blob(our_entry)
        their_blob = entry_blob(their_entry)

        if our_blob == their_blob:
            selected = our_entry
        elif base_blob == our_blob:
            selected = their_entry
        elif base_blob == their_blob:
            selected = our_entry
        else:
            conflicts.append(path)
            continue

        if selected is not None:
            merged[path] = selected

    return merged, conflicts


def entry_blob(entry):

    return entry["blob"] if entry is not None else None


def is_ancestor(ancestor, descendant, root=None):

    return ancestor in ancestors_of(descendant, root)


def common_ancestor(first, second, root=None):

    first_ancestors = ancestors_of(first, root)
    for commit_id in commit_walk(second, root):
        if commit_id in first_ancestors:
            return commit_id

    return None


def ancestors_of(commit_id, root=None):

    return set(commit_walk(commit_id, root))


def commit_walk(start, root=None):

    pending = [start] if start else []
    visited = set()

    while pending:
        commit_id = pending.pop()
        if commit_id in visited:
            continue

        visited.add(commit_id)
        yield commit_id

        data = load_commit(commit_id, root)
        parent = data.get("parent")
        merge_parent = data.get("merge_parent")
        if parent:
            pending.append(parent)
        if merge_parent:
            pending.append(merge_parent)


def write_working_tree(target_tree, root=None):
    """Materialise a tracked tree after local-change protection has run."""

    root = Path(root or Path.cwd()).resolve()
    existing_tree = current_tree(root)

    for path in set(existing_tree) - set(target_tree):
        file_path = root / path
        if file_path.exists():
            file_path.unlink()

    for path, entry in target_tree.items():
        destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(blob_path(entry["blob"], root), destination)


def working_changes(root=None):
    """Return tracked files whose working copy differs from the active branch."""

    root = Path(root or Path.cwd()).resolve()
    changes = []

    for path, entry in current_tree(root).items():
        file_path = root / path
        if not file_path.exists() or file_path.read_bytes() != blob_path(entry["blob"], root).read_bytes():
            changes.append(path)

    return sorted(changes)


def normalise_relative_path(file_path, root):

    source = Path(file_path).resolve()
    try:
        return source.relative_to(root).as_posix()
    except ValueError as error:
        raise RepositoryError("Only files inside this repository can be used.") from error


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
