import docker
import pytest


@pytest.fixture(scope="module")
def client():
    return docker.from_env()


@pytest.mark.parametrize("version", ("3.9", "3.10", "3.11", "3.12", "3.13"))
def test_python_version_compatibility(version, client):
    image_tag = f"pkonfig:{version}"
    # Build the image for the specific Python version
    client.images.build(
        path=".",
        tag=image_tag,
        rm=True,
        buildargs={"VERSION": version},
        nocache=True,
    )

    # Run unit tests inside the container and capture stdout/stderr from docker SDK.
    logs = client.containers.run(
        image=image_tag,
        remove=True,
    )
    out = logs.decode("utf-8", errors="replace") if isinstance(logs, (bytes, bytearray)) else str(logs)
    # Ensure there are no failures reported by pytest inside the container
    assert "failed" not in out.lower(), f"Unit tests reported failures in Python {version}:\n{out}"
