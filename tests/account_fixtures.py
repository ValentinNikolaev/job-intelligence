"""Explicit account descriptors for isolated operational-boundary tests."""
from pathlib import Path


def write_account_config(root: Path) -> Path:
    """Write only the public descriptor, without touching secrets or linked inputs."""
    target = Path(root) / "config/accounts.yaml"
    content = (Path(__file__).resolve().parents[1] / "config/accounts.yaml").read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.is_file() or target.read_bytes() != content:
        target.write_bytes(content)
    return target
