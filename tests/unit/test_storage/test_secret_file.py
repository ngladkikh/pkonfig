import json
from collections import ChainMap

import pytest

from pkonfig.storage import DictStorage, SecretFile


def test_secret_file_reads_directory(tmp_path):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "api_key.txt").write_text("super-secret", encoding="utf-8")
    (secrets_dir / "token").write_text("abc123", encoding="utf-8")

    storage = SecretFile(secrets_dir)

    assert storage[("api_key",)] == "super-secret"
    assert storage[("token",)] == "abc123"


def test_secret_file_reads_single_file(tmp_path):
    secret_file = tmp_path / "database_password.secret"
    secret_file.write_text("hunter2", encoding="utf-8")

    storage = SecretFile(secret_file)

    assert storage[("database_password",)] == "hunter2"


def test_secret_file_reads_vault_kv_v2_json_file(tmp_path):
    secret_file = tmp_path / "vault-export.json"
    secret_file.write_text(
        json.dumps(
            {
                "request_id": "req-123",
                "data": {
                    "data": {
                        "database": {"password": "hunter2"},
                        "api_key": "super-secret",
                    },
                    "metadata": {"version": 1},
                },
            }
        ),
        encoding="utf-8",
    )

    storage = SecretFile(secret_file)

    assert storage[("database", "password")] == "hunter2"
    assert storage[("api_key",)] == "super-secret"
    with pytest.raises(KeyError):
        storage[("vault-export",)]


def test_secret_file_reads_vault_kv_json_from_directory(tmp_path):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "vault.json").write_text(
        json.dumps(
            {
                "request_id": "req-123",
                "data": {
                    "data": {"service": {"token": "abc123"}},
                    "metadata": {"version": 1},
                },
            }
        ),
        encoding="utf-8",
    )
    (secrets_dir / "username").write_text("alice", encoding="utf-8")

    storage = SecretFile(secrets_dir)

    assert storage[("service", "token")] == "abc123"
    assert storage[("username",)] == "alice"


def test_secret_file_reads_vault_kv_v1_json_file(tmp_path):
    secret_file = tmp_path / "vault-kv1.json"
    secret_file.write_text(
        json.dumps(
            {
                "request_id": "req-123",
                "lease_id": "",
                "renewable": False,
                "lease_duration": 0,
                "data": {
                    "database": {"password": "hunter2"},
                    "api_key": "super-secret",
                },
            }
        ),
        encoding="utf-8",
    )

    storage = SecretFile(secret_file)

    assert storage[("database", "password")] == "hunter2"
    assert storage[("api_key",)] == "super-secret"


def test_secret_file_respects_defaults(tmp_path):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "username").write_text("alice", encoding="utf-8")

    storage = SecretFile(secrets_dir, password="fallback")

    assert storage[("username",)] == "alice"
    assert storage[("password",)] == "fallback"


def test_secret_file_supports_chainmap_priority(tmp_path):
    secrets_dir = tmp_path / "secrets"
    secrets_dir.mkdir()
    (secrets_dir / "api_key").write_text("file-secret", encoding="utf-8")

    storage = ChainMap(
        DictStorage(api_key="override-secret"),
        SecretFile(secrets_dir),
    )

    assert storage[("api_key",)] == "override-secret"


def test_missing_secret_file_raises_exception():
    with pytest.raises(FileNotFoundError):
        SecretFile("not_exists", missing_ok=False)


def test_missing_secret_file_is_allowed_when_missing_ok():
    storage = SecretFile("not_exists", missing_ok=True, api_key="fallback")

    assert storage[("api_key",)] == "fallback"
