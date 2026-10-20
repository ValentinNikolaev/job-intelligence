"""Resolve the single supported account before operational work begins."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


ACCOUNT_ENVIRONMENT_VARIABLE = "JOBINTEL_ACCOUNT"
ACCOUNT_DESCRIPTOR = "config/accounts.yaml"
_REFERENCES = (
    ("selection_policy", "config/selection-policy.yaml"),
    ("matching_policy", "config/matching-policy.yaml"),
    ("application_profile", "config/application-profile.yaml"),
    ("application_review", "config/application-review.yaml"),
    ("editorial_knowledge", "config/cv-editorial-knowledge.yaml"),
    ("workflow_policy", "config/codex-workflows.yaml"),
    ("data_services", "config/data-services.yaml"),
)
_PATHS = (
    ("sources", "sources"),
    ("registry", "registry"),
    ("catalog", "catalog"),
    ("archives", "archives"),
    ("notifications", "notifications/telegram"),
    ("work", ".codex-work"),
    ("environment", "sources/.env"),
)


class AccountConfigurationError(ValueError):
    """The requested account cannot be resolved safely."""


def _root(project_root: Path) -> Path:
    try:
        root = Path(project_root).resolve()
        if not root.is_dir():
            raise AccountConfigurationError("account project root must be an existing directory")
        return root
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        if isinstance(exc, AccountConfigurationError):
            raise
        raise AccountConfigurationError("cannot resolve account project root") from None


def _contained(root: Path, relative: str) -> Path:
    if (type(relative) is not str or not relative or "\\" in relative
            or relative.startswith("/") or re.match(r"^[A-Za-z]:", relative)
            or any(part in {"", ".", ".."} for part in relative.split("/"))):
        raise AccountConfigurationError("account paths must be contained project-relative POSIX paths")
    try:
        target = (root / relative).resolve()
    except (OSError, RuntimeError, ValueError):
        raise AccountConfigurationError("cannot resolve an account path") from None
    if not target.is_relative_to(root):
        raise AccountConfigurationError("account path escapes the project root")
    if target != root / relative:
        raise AccountConfigurationError("account schema-1 paths cannot be redirected")
    return target


@dataclass(frozen=True, slots=True)
class AccountContext:
    project_root: Path
    account_id: str
    descriptor_path: Path
    references: tuple[tuple[str, str], ...]
    paths: tuple[tuple[str, str], ...]
    descriptor_sha256: str

    def reference(self, name: str) -> Path:
        try:
            relative = dict(self.references)[name]
        except (KeyError, TypeError):
            raise AccountConfigurationError("unknown account configuration reference") from None
        return _contained(self.project_root, relative)

    def path(self, name: str) -> Path:
        try:
            relative = dict(self.paths)[name]
        except (KeyError, TypeError):
            raise AccountConfigurationError("unknown account data path") from None
        return _contained(self.project_root, relative)

    def require_root(self, root: Path) -> None:
        if _root(root) != self.project_root:
            raise AccountConfigurationError("account context belongs to another project root")


def _selector(value: str) -> str:
    if (type(value) is not str or value != value.strip()
            or re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", value) is None):
        raise AccountConfigurationError("account selector must be a nonempty lowercase identifier")
    return value


def extract_account_selector(argv: Sequence[str]) -> tuple[str | None, list[str]]:
    """Remove account options before dispatch; leave arguments after ``--`` intact."""
    selected = None
    remaining: list[str] = []
    index = 0
    while index < len(argv):
        argument = argv[index]
        if type(argument) is not str:
            raise AccountConfigurationError("command arguments must be text")
        if argument == "--":
            remaining.extend(argv[index:])
            break
        if argument == "--account":
            index += 1
            if index == len(argv) or type(argv[index]) is not str or argv[index].startswith("-"):
                raise AccountConfigurationError("--account requires an account identifier")
            value = argv[index]
        elif argument.startswith("--account="):
            value = argument[len("--account="):]
        else:
            remaining.append(argument)
            index += 1
            continue
        value = _selector(value)
        if selected is not None and selected != value:
            raise AccountConfigurationError("conflicting command-line account selectors")
        selected = value
        index += 1
    return selected, remaining


def _check_yaml(node: Node, ancestors: frozenset[int] = frozenset()) -> None:
    if id(node) in ancestors:
        raise AccountConfigurationError("account descriptor contains recursive YAML aliases")
    ancestors = ancestors | {id(node)}
    if isinstance(node, MappingNode):
        seen: set[str] = set()
        for key, value in node.value:
            if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                raise AccountConfigurationError("account descriptor keys must be text")
            if key.value in seen:
                raise AccountConfigurationError("account descriptor contains duplicate YAML keys")
            seen.add(key.value)
            _check_yaml(value, ancestors)
    elif isinstance(node, SequenceNode):
        for child in node.value:
            _check_yaml(child, ancestors)


def _mapping(value: object, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise AccountConfigurationError(f"{label} has missing or unsupported fields")
    return value


def _pinned(value: object, expected: tuple[tuple[str, str], ...], label: str) -> None:
    loaded = _mapping(value, {name for name, _ in expected}, label)
    if any(type(loaded[name]) is not str or loaded[name] != path for name, path in expected):
        raise AccountConfigurationError(f"{label} must use the supported schema-1 paths")


def load_account_context(
    project_root: Path,
    *,
    account: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> AccountContext:
    """Read only the selected root's descriptor and inspect path containment.

    CLI and process-environment selections must agree when both are present.
    Dotenv and referenced configuration files are left to operational consumers.
    """
    environment = os.environ if environ is None else environ
    requested = _selector(account) if account is not None else None
    environment_account = environment.get(ACCOUNT_ENVIRONMENT_VARIABLE)
    if environment_account is not None:
        environment_account = _selector(environment_account)
    if requested is not None and environment_account is not None and requested != environment_account:
        raise AccountConfigurationError("command-line and environment account selectors disagree")
    selected = requested if requested is not None else environment_account
    if selected is not None and selected != "current":
        raise AccountConfigurationError("requested account is not enabled")

    root = _root(project_root)
    descriptor = _contained(root, ACCOUNT_DESCRIPTOR)
    try:
        raw = descriptor.read_bytes()
        text = raw.decode("utf-8-sig")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            _check_yaml(node)
        loaded = yaml.safe_load(text)
    except (OSError, UnicodeError):
        raise AccountConfigurationError("cannot read UTF-8 account descriptor config/accounts.yaml") from None
    except yaml.YAMLError:
        raise AccountConfigurationError("account descriptor contains malformed or unsupported YAML") from None
    loaded = _mapping(loaded, {"schema_version", "default_account", "accounts"}, "account descriptor")
    if type(loaded["schema_version"]) is not int or loaded["schema_version"] != 1:
        raise AccountConfigurationError("account descriptor requires schema_version 1")
    if loaded["default_account"] != "current":
        raise AccountConfigurationError("account descriptor default must be current")
    accounts = _mapping(loaded["accounts"], {"current"}, "account list")
    current = _mapping(accounts["current"], {"references", "paths"}, "current account")
    _pinned(current["references"], _REFERENCES, "account references")
    _pinned(current["paths"], _PATHS, "account paths")
    for _, relative in (*_REFERENCES, *_PATHS):
        _contained(root, relative)
    return AccountContext(
        project_root=root,
        account_id="current",
        descriptor_path=descriptor,
        references=_REFERENCES,
        paths=_PATHS,
        descriptor_sha256=hashlib.sha256(raw).hexdigest(),
    )


def require_account_context(
    project_root: Path,
    context: AccountContext | None = None,
    *,
    account: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> AccountContext:
    """Reload the authority before work and reject a stale or mismatched snapshot."""
    current = load_account_context(project_root, account=account, environ=environ)
    if context is not None:
        if not isinstance(context, AccountContext):
            raise AccountConfigurationError("invalid account context")
        context.require_root(current.project_root)
        if context != current:
            raise AccountConfigurationError("account context is stale for the current descriptor")
    return current


def main(argv: Sequence[str] | None = None) -> int:
    """Validate account control-plane configuration without operational access."""
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--account", help="account identifier (default: current)")
    try:
        account, remaining = extract_account_selector(list(sys.argv[1:] if argv is None else argv))
        args = parser.parse_args(remaining)
        context = load_account_context(args.project_root, account=account)
    except AccountConfigurationError as exc:
        print(f"Account configuration error: {exc}", file=sys.stderr)
        return 2
    print(context.account_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
