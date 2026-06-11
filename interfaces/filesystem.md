# Filesystem Interface

> The Filesystem interface defines how SELF stores and retrieves raw artifacts on disk. It is one of four storage substrates (alongside DuckDB, graph store, and vector index).

## Purpose

The filesystem is used for unstructured or binary data that does not fit well in a database:
- Raw observation payloads (content-addressable)
- Memory snapshots
- Configuration files
- Log files
- Backup archives
- Exported state bundles

## Directory Layout

```
~/.config/self/
├── config.yaml                  # User configuration
├── secrets/                     # Encrypted secrets storage
│   └── secrets.json
│
~/.local/share/self/
├── artifacts/                   # Content-addressable raw payloads
│   └── <sha256_prefix>/
│       └── <sha256_full>
├── snapshots/                   # Point-in-time memory snapshots
│   └── <snapshot_id>/
│       ├── manifest.json        # Snapshot manifest
│       ├── events.json
│       ├── knowledge.json
│       ├── audit_log.json
│       └── integrity.sha256
├── exports/                     # Portable export bundles
│   └── <export_id>/
│       ├── self-export.json
│       └── integrity.sha256
├── audit_head.sha256            # Current audit log hash chain head
│
~/.local/state/self/
├── logs/                        # Application logs
│   ├── self.log
│   └── self.error.log
├── metrics/                     # Metrics dumps
│   └── metrics.json
│
~/.cache/self/
└── vector_index/                # FAISS vector index files
    ├── index.faiss
    └── index.mapping.json
```

## Core Operations

```python
def read(path: str) -> bytes
```
Reads a file from the filesystem.

```python
def write(path: str, data: bytes) -> str
```
Writes data to a file. Returns the SHA-256 hash of the content.

```python
def delete(path: str) -> None
```
Deletes a file. Logs the deletion.

```python
def exists(path: str) -> bool
```
Checks whether a path exists.

```python
def list_dir(path: str) -> list[str]
```
Lists entries in a directory.

```python
def content_addressable_store(data: bytes) -> str
```
Stores data under its SHA-256 hash. Returns the hash. Used for raw observation payloads.

## Governance

- **Locality**: All filesystem data resides on the user's local hardware by default.
- **Auditability**: File deletions are logged.
- **Integrity**: Content-addressable storage ensures data cannot be modified without detection.
- **Backup**: The entire `~/.local/share/self/` directory can be backed up as a unit.

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SELF_CONFIG_DIR` | `~/.config/self` | Configuration directory |
| `SELF_DATA_DIR` | `~/.local/share/self` | Data directory |
| `SELF_STATE_DIR` | `~/.local/state/self` | State directory |
| `SELF_CACHE_DIR` | `~/.cache/self` | Cache directory |

Paths can be overridden via the `config.yaml` file.
