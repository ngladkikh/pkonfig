import os
from time import time

import pydantic
from pkonfig.config import Config, EmbeddedConfig
from pkonfig.fields import Float
from pkonfig.storage import Env


def read_py(kwargs):
    class InnerPy(pydantic.BaseModel):
        i: int
        f: float

    class Settings(pydantic.BaseSettings):
        inner: InnerPy
        s = 'test'

        class Config:
            env_prefix = 'APP_'
            env_nested_delimiter = '__'
            case_sensitive = False

    return Settings(**kwargs)


def get_attributes_py(settings):
    settings.s
    settings.inner.i
    settings.inner.f


def read_pk(kwargs):
    class Inner(EmbeddedConfig):
        i: int
        f = Float()

    class Settings(Config):
        s: str
        inner = Inner()

    return Settings(kwargs)


def main():
    iterations = 500
    kwargs = {
        "s": "some",
        "inner": {
            "i": 1,
            "f": 0.2
        }
    }
    test_pydantic_read(iterations, kwargs)
    test_pkonfig_read(iterations, kwargs)

    test_pydantic_getter(iterations, kwargs)
    test_pkonfig_getter(iterations, kwargs)

    os.environ["APP_S"] = "some"
    os.environ["APP_INNER__I"] = "1"
    os.environ["APP_INNER__F"] = "0.2"

    storage = Env()
    test_pkonfig_read(iterations, storage)
    test_pydantic_read(iterations, {})


def test_pkonfig_getter(iterations, kwargs):
    start = time()
    s_py = read_pk(kwargs)
    for _ in range(iterations):
        get_attributes_py(s_py)
    print(f"PKonfig attributes read: {(time() - start)}")


def test_pydantic_getter(iterations, kwargs):
    start = time()
    s_py = read_py(kwargs)
    for _ in range(iterations):
        get_attributes_py(s_py)
    print(f"PyDantic attributes read: {(time() - start)}")


def test_pkonfig_read(iterations, kwargs):
    start = time()
    for _ in range(iterations):
        read_pk(kwargs)
    print(f"PKonfig read: {time() - start}")


def test_pydantic_read(iterations, kwargs):
    start = time()
    for _ in range(iterations):
        read_py(kwargs)
    print(f"PyDantic read: {time() - start}")


if __name__ == "__main__":
    main()
