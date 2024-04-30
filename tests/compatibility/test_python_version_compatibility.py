import docker
import pytest


@pytest.fixture(scope="module")
def client():
    return docker.from_env()


@pytest.mark.parametrize("version", ("3.9", "3.10", "3.11", "3.12"))
def test_python_version_compatibility(version, client):
    image_tag = f"pkonfig:{version}"
    client.images.build(
        path=".",
        tag=image_tag,
        rm=True,
        buildargs={"VERSION": version},
        nocache=True,
    )
    client.containers.run(image=image_tag, remove=True)
