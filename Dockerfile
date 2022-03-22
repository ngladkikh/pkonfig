ARG VERSION
FROM python:$VERSION-slim

RUN pip install pytest tomli pyyaml typing_extensions

COPY . .

CMD python3 -m pytest -q tests
